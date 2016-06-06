#encoding:utf-8
from mc.models import Paper, PaperDiff, QuestionDiff, PaperAudit
from mc.models import enums
from service.core import _checkpoint, _question, _report
from survey import survey_utils
import DbUtils
def do_dealer_paper_diff(paper, user):
    '''这个方法仅供问卷终审时调用，
            检查所对应的经销商的两份paper，是否都已经终审提交，
            若有才检查问卷差异；
            若没有都终审，则不作比较
    '''
    dealer = paper.dealer
    term = paper.term
    project = paper.project
    status = enums.PAPER_STATUS_FINISH
    paper_types = [enums.FW_PAPER_TYPE, enums.FH_PAPER_TYPE]
    results = Paper.objects.filter(term=term, project=project, dealer=dealer, status=status, paper_type__in=paper_types).order_by('-id')
    if len(results) < 2:
        return None, None
    paper_type_dict = {}
    
    def _paper_replace(p, type, paper_type_dict):
        '''当同种类型有多条paper，仅保存id号最大的那条'''
        if p.paper_type == type:
            old = paper_type_dict.get(type)
            if old and old.id >= p.id:
                pass
            else:
                paper_type_dict[p.paper_type] = p
            
    for p in results:
        _paper_replace(p, enums.FW_PAPER_TYPE, paper_type_dict)
        _paper_replace(p, enums.FH_PAPER_TYPE, paper_type_dict)
            
    #若两种类型的问卷未都终审，不作差异比较
    if len(paper_type_dict) != 2:
        return None, None
    #问卷差异，仅比较选择题
    cp_list = _checkpoint.get_project_sub_cp_score_list(project) #获得检查点仅A－F环节的检查点
    fw_paper = paper_type_dict.get(enums.FW_PAPER_TYPE) #FW团队的问卷
    fh_paper = paper_type_dict.get(enums.FH_PAPER_TYPE) #独立审核的问卷
    fw_asnwer_dict = survey_utils.get_respondentdata_dict_by_paper(fw_paper) #FW问卷的答案
    fh_asnwer_dict = survey_utils.get_respondentdata_dict_by_paper(fh_paper)#独立审核的答案
    fw_score_dict = survey_utils.get_reportdata_dict_by_paper(fw_paper)#FW问卷的得分
    fh_score_dict = survey_utils.get_reportdata_dict_by_paper(fh_paper)#独立审核的得分
    if fw_score_dict is None or fh_score_dict is None:
        return None, None
    no_conflict = True #最终是否有差异
    paperdiff = None
    diff_list = [] #差异题目
    for cp in cp_list:
        qcid = cp.name # qcid = cp.resp_col
        v1 = fw_asnwer_dict.get(qcid)
        v2 = fh_asnwer_dict.get(qcid)
        #同为None，不比较
        if v1 is None and v2 is None:
            continue
        tmp_flag = True
        #有1值为None，为不同
        if v1 is None and v2 is not None:
            tmp_flag = False
        if v1 is not None and v2 is None:
            tmp_flag = False
        #都不为None, 比较值
        if v1 is not None and v2 is not None:
            tmp_flag = v1 == v2
        
        if tmp_flag == False:
            diff_list.append(qcid)
            if paperdiff is None:
                #删除以前有的问卷差异
                paperdiff, created = PaperDiff.objects.get_or_create(fw_paper=fw_paper, fh_paper=fh_paper)
                if  created == False:
                    question_diffs = QuestionDiff.objects.filter(paper_diff=paperdiff)
                    for qd in question_diffs:
                        qd.delete()
                    paperdiff.delete()
                    paperdiff, created = PaperDiff.objects.get_or_create(fw_paper=fw_paper, fh_paper=fh_paper)
                paperdiff.status = enums.HAS_CONFLICT
                paperdiff.save()
            question = _question.get_question_by_cid(project, qcid)
            questiondiff, created = QuestionDiff.objects.get_or_create(paper_diff=paperdiff, question=question)
            questiondiff.fw_q_score = fw_score_dict.get(qcid)
            fw_comm = fw_asnwer_dict.get('%s__open' % qcid)
            tran1 = fw_paper.respondent.get_translation(qcid)
            if fw_comm is None:
                fw_comm = ''
            if tran1 is None:
                tran1 = ''
            questiondiff.fw_q_comment = '%s<br>%s' % (fw_comm, tran1)
            questiondiff.fh_q_score = fh_score_dict.get(qcid)
            fh_comm = fh_asnwer_dict.get('%s__open' % qcid)
            tran2 = fh_paper.respondent.get_translation(qcid)
            if fh_comm is None:
                fh_comm = ''
            if tran2 is None:
                tran2 = ''
            questiondiff.fh_q_comment = '%s<br>%s' % (fh_comm, tran2)
            questiondiff.save()
            no_conflict = False
    
    diff_status = enums.HAS_CONFLICT
    if no_conflict:
        diff_status = enums.ABSOLUTELY_MATCH
    #忽略有差异题目
    #创建BMW审核问卷，答案用GFK团队的，此为最终问卷，前台一律采用此问卷数据
    #1. copy BMW paper，可能已经存在（原来问卷，重复做终审,那么只能做全字段更新，以保证无脏数据）
    bmw_paper, created = Paper.objects.get_or_create(project=project, user=fw_paper.user, dealer=dealer, term=term, status=status, paper_type=enums.BMW_PAPER_TYPE)
    bmw_paper.visitor_num = fw_paper.visitor_num
    bmw_paper.survey_code = fw_paper.survey_code
    bmw_paper.visit_begin = fw_paper.visit_begin
    bmw_paper.visit_end = fw_paper.visit_end
    bmw_paper.is_public = fw_paper.is_public
    bmw_paper.score = fw_paper.score
    bmw_paper.save()
    if no_conflict:
        #2. 创建paperdiff记录，以记录比对的paper关系
        paperdiff, created = PaperDiff.objects.get_or_create(fw_paper=fw_paper, fh_paper=fh_paper)
        if created == False:
            question_diffs = QuestionDiff.objects.filter(paper_diff=paperdiff)
            for qd in question_diffs:
                qd.delete()
            paperdiff.delete()
            paperdiff, created = PaperDiff.objects.get_or_create(fw_paper=fw_paper, fh_paper=fh_paper)
    paperdiff.final_paper = bmw_paper
    paperdiff.status = diff_status
    paperdiff.save()
        
    #3. copy BMW paper respondent
    #BMW的respondent可能已经存在，但不能使用gfk或fh的respondent，这里必须创建
    respondent = bmw_paper.respondent
    resp_created = False
    if  respondent is None:
        from survey.models import Respondent
        respondent = Respondent()
        resp_created = True
    respondent.project = fw_paper.respondent.project
    respondent.status = fw_paper.respondent.status
    respondent.user = fw_paper.respondent.user
    respondent.start_time = fw_paper.respondent.start_time
    respondent.finish_time = fw_paper.respondent.finish_time
    respondent.save()
    try:
        c, con = DbUtils.cursor()
        if resp_created:
            bmw_paper.respondent = respondent
            bmw_paper.save()
            #若respondent为创建，则respondentdata一定不存在，直接先插条仅id值记录，然后只要做更新列值
            insert_surveydt_sql = 'insert into survey_respondentdata (id) values(%s)' % str(respondent.id)
            c.execute(insert_surveydt_sql)
            if con:
                con.commit()
        #可能是第2次做终审，survey_respondentdata, report, report_data会已经存在，
        #3. 更新 survey_respondentdata
        #去掉FW的respondent_data字典的id，其它列值copy
        if fw_asnwer_dict.has_key('id'):
            fw_asnwer_dict.pop('id')
        
        for key in fw_asnwer_dict.keys():
            val = fw_asnwer_dict.get(key, 'null')
            if val is None or  key in diff_list: #忽略差异题目
                val = 'null'
            fw_asnwer_dict[key] = val
        #全列值更新，需要测试null值字段是否存在
        size = len(fw_asnwer_dict)
        update_fields = 20
        lefts = size % update_fields
        times = size / update_fields
        if lefts:
            times += 1
        key_list = fw_asnwer_dict.keys()
        for i in  range(0, times):
            part_dict = {}
            start = i * update_fields
            end = start + update_fields
            part_keys = key_list[start: end]
            for key in part_keys:
                val = fw_asnwer_dict.get(key, 'null') 
                fw_asnwer_dict.pop(key, 0)
                if  isinstance(val, str)  or isinstance(val, unicode) :
                    if val != 'null':
                        val = '"%s"' % val
                part_dict[key] = val
            sql_str = ','.join(['%s=%%(%s)s' % (key, key) for key in part_dict])
            sql = "update survey_respondentdata set %s where id=%s" % (sql_str, respondent.id)    
            sql = sql % part_dict
            c.execute(sql)
            if con:
                con.commit()
        #4. copy report 及 report_data
        report_data_dict = survey_utils.get_reportdata_dict_by_paper(fw_paper)
        if report_data_dict.has_key('id'):
            report_data_dict.pop('id')
        for key in report_data_dict.keys():
            val = report_data_dict[key]
            if val is None:
                val = 'null'
            report_data_dict[key] = val
            if key == 'T3':
                report_data_dict[key] = '"%s"' % val
        _report.update_one_project_papers_report(bmw_paper, report_data_dict, c, con)
        #若有冲突，则不用保存分数
        if no_conflict == False:
            bmw_paper.score = None
            bmw_paper.save()
        #5. copy FW的translation
        translations_dict = fw_paper.respondent.get_translations()
        respondent.set_translations(translations_dict)
        #6. copy paper audit信息
        audits = PaperAudit.objects.filter(paper=fw_paper)
        for audit in audits:
            u = audit.user
            if audit.new_status == enums.PAPER_STATUS_FINISH:
                u = user
            pa, create = PaperAudit.objects.get_or_create(paper=bmw_paper, new_status=audit.new_status)
            pa.old_status = audit.old_status
            pa.user = u
            pa.save() 
    finally:
        if c:
            c.close()
        if con:
            con.close() 
        
    return no_conflict, paperdiff
        
        
            
    
    
