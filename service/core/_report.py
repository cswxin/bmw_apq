#encoding:utf-8
import time, os, sys
sys.path.insert(0, os.path.abspath(os.curdir))
from django.db.transaction import commit_on_success, set_dirty
from mc.models import Report, Dealer, DealerType, OtherReport, Project , Term
from survey.models import CheckPoint, Alternative
from mc import enums
from service.core import _checkpoint, _alternative, _dealer, _term, _project, _question, _user, _paper
import constant
import copy
from survey import survey_utils
import DbUtils

def get_dealer_sub_score(term, dealer, project, dealertype):
    '''
    对于经销商来说，dealertype就是自己的所属的品牌
    对于层级dealer（全国，区域，小区，城市，集团）来说，dealertype 可能是MINI，BMW，Audi，Lexus，Mercedes-Benz
    paper_type: BMW,MINI�BMW类型；竞�Audi，Lexus，Mercedes-Benz)用GFK类型
    '''
    query = Report.objects.filter(term=term, dealer=dealer, project=project, dealertype=dealertype).order_by('-id')
    if len(query) == 0:
        return None
    else:
        report = query[0]
        return get_report_sub_score(report.id, project.id)

#大区
def get_region_sub_score(term, dealer, project, dealertype):
    d = _dealer.get_dealer_parent_by_level(dealer, constant.LEVEL_DAQU)
    query = Report.objects.filter(term=term, dealer=d, project=project, dealertype=dealertype).order_by('-id')
    if len(query) == 0:
        return None
    else:
        report = query[0]
    return get_report_sub_score(report.id, project.id)

#全国
def get_national_sub_score(term, dealer, project, dealertype):
    d = _dealer.get_dealer_parent_by_level(dealer, constant.LEVEL_NATION)
    query = Report.objects.filter(term=term, dealer=d, project=project, dealertype=dealertype).order_by('-id')
    if len(query) == 0:
        return None
    else:
        report = query[0]
    return get_report_sub_score(report.id, project.id)

#小区
def get_xq_sub_score(term, dealer, project, dealertype):
    d = _dealer.get_dealer_parent_by_level(dealer, constant.LEVEL_XQ)
    query = Report.objects.filter(term=term, dealer=d, project=project, dealertype=dealertype).order_by('-id')
    if len(query) == 0:
        return None
    else:
        report = query[0]
    return get_report_sub_score(report.id, project.id)

#城市
def get_city_sub_score(term, dealer, project, dealertype):
    d = _dealer.get_dealer_parent_by_level(dealer, constant.LEVEL_CITY)
    query = Report.objects.filter(term=term, dealer=d, project=project, dealertype=dealertype).order_by('-id')
    if len(query) == 0:
        return None
    else:
        report = query[0]
    return get_report_sub_score(report.id, project.id)

#省份
def get_province_sub_score(term, dealer, project, dealertype):
    d = _dealer.get_dealer_parent_by_level(dealer, constant.LEVEL_PROVINCE)
    query = Report.objects.filter(term=term, dealer=d, project=project, dealertype=dealertype).order_by('-id')
    if len(query) == 0:
        return None
    else:
        report = query[0]
    return get_report_sub_score(report.id, project.id)

#经销商集�
def get_jt_sub_score(term, dealer, project, dealertype):
    d = _dealer.get_dealer_parent_by_level(dealer, constant.LEVEL_JT)
    query = Report.objects.filter(term=term, dealer=d, project=project, dealertype=dealertype).order_by('-id')
    if len(query) == 0:
        return None
    else:
        report = query[0]
    return get_report_sub_score(report.id, project.id)

def get_dealer_score(term, dealer, project, dealertype, column_list=None):
    query = Report.objects.filter(term=term, dealer=dealer, project=project, dealertype=dealertype).order_by('-id')
    if len(query) > 0:
        report = query[0]
        return get_report_score(report.id, project.id, column_list)
    else:
        return None
    
#def get_dealer_score(term, dealer, dealertype):
#    query = Report.objects.filter(term=term, dealer=dealer, dealertype=dealertype).order_by('-id')
#    if len(query) > 0:
#        report = query[0]
#        return report.score
#    else:
#        return None
    
def get_dealer_group_score(term, dealer, project, dealertype):
    query = Report.objects.filter(term=term, dealer=dealer, project=project, dealertype=dealertype).order_by('-id')
    if len(query) > 0:
        report = query[0]
        return get_report_group_score(report.id, project.id)
    else:
        return None
    
def get_region_score(term, dealer, project, dealertype, column_list=None):
    d = _dealer.get_dealer_parent_by_level(dealer, constant.LEVEL_DAQU)
    query = Report.objects.filter(term=term, dealer=d, project=project, dealertype=dealertype).order_by('-id')
    #print len(query)
    if len(query) == 0:
        return None
    else:
        report = query[0]
    return get_report_score(report.id, project.id, column_list)

def get_national_score(term, dealer, project, dealertype, column_list=None):
    d = _dealer.get_dealer_parent_by_level(dealer, constant.LEVEL_NATION)
    query = Report.objects.filter(term=term, dealer=d, project=project, dealertype=dealertype).order_by('-id')
    if len(query) == 0:
        return None
    else:
        report = query[0]
    return get_report_score(report.id, project.id, column_list)

def get_xq_score(term, dealer, project, dealertype, column_list=None):
    d = _dealer.get_dealer_parent_by_level(dealer, constant.LEVEL_XQ)
    query = Report.objects.filter(term=term, dealer=d, project=project, dealertype=dealertype).order_by('-id')
    if len(query) == 0:
        return None
    else:
        report = query[0]
    return get_report_score(report.id, project.id, column_list)

def get_city_score(term, dealer, project, dealertype, column_list=None):
    d = _dealer.get_dealer_parent_by_level(dealer, constant.LEVEL_CITY)
    query = Report.objects.filter(term=term, dealer=d, project=project, dealertype=dealertype).order_by('-id')
    if len(query) == 0:
        return None
    else:
        report = query[0]
    return get_report_score(report.id, project.id, column_list)

def get_province_score(term, dealer, project, dealertype, column_list=None):
    d = _dealer.get_dealer_parent_by_level(dealer, constant.LEVEL_PROVINCE)
    query = Report.objects.filter(term=term, dealer=d, project=project, dealertype=dealertype).order_by('-id')
    if len(query) == 0:
        return None
    else:
        report = query[0]
    return get_report_score(report.id, project.id, column_list)

def get_jt_score(term, dealer, project, dealertype, column_list=None):
    d = _dealer.get_dealer_parent_by_level(dealer, constant.LEVEL_JT)
    query = Report.objects.filter(term=term, dealer=d, project=project, dealertype=dealertype).order_by('-id')
    if len(query) == 0:
        return None
    else:
        report = query[0]
    return get_report_score(report.id, project.id, column_list)

def get_report_score(report_id, project_id, column_list=None):
    project = _project.get_project_by_id(project_id)
    if not column_list:
        column_str = get_main_score_column_str(project)
    else:
        column_str = ','.join(column_list)
    sql = 'select %s from mc_reportdata where id=%s;' % (column_str, report_id)
    try:
        c, con = DbUtils.cursor()
        c.execute(sql)
        ret = c.fetchone()
    finally:
        if c:
            c.close()
        if con:
            con.close() 
    if ret:
        return [score or 0 for score in ret]
    
    return None

#根据检查点和paper取出得分
def get_report_score_by_cplist_paper(cplist, paper):
    query = Report.objects.filter(respondent=paper.respondent)
    if len(query) == 0:
        return None
    else:
        report = query[0]
    
    cps = []
    for cp in cplist:
        if cp.name == 'Total':
            cps.append('total')
        else:
            cps.append(cp.name)
    cps_str = ','.join(cps)
    sql = 'select %s from mc_reportdata where id=%s;' % (cps_str, report.id)
    try:
        c, con = DbUtils.cursor()
        c.execute(sql)
        ret = c.fetchone()
    finally:
        if c:
            c.close()
        if con:
            con.close() 
    if ret:
        return [score or 0 for score in ret]
    
    return None

#在paper对象中放入检查点和问题的分数
def set_score_in_papers(cplist, papers):
    for paper in papers:
        paper.score_list = get_report_score_by_cplist_paper(cplist, paper)

def get_report_group_score(report_id, project_id, has_min_max=False):
    project = _project.get_project_by_id(project_id)
    cp_group_list_str = get_main_group_score_column_str(project, has_min_max)
    return get_report_group_score_0(report_id, cp_group_list_str)

def get_report_group_score_0(report_id, cp_group_list_str):
    sql = 'select %s from mc_reportdata where id=%s;' % (cp_group_list_str, report_id)
    try:
        c, con = DbUtils.cursor()
        c.execute(sql)
        ret = c.fetchone()
    finally:
        if c:
            c.close()
        if con:
            con.close() 
    if ret:
        return [score or 0 for score in ret]
    
    return None

def get_report_sub_score(report_id, project_id):
    sql = 'select %s from mc_reportdata where id=%s;' % (get_sub_score_column_str(project_id), report_id)
    try:
        c, con = DbUtils.cursor()
        c.execute(sql)
        cur = c.fetchone()
    finally:
        if c:
            c.close()
        if con:
            con.close() 
    return cur

def get_brand_report_sub_score(report, sub_checkpoint_list):
    project = report.project
    report_id = report.id
    columstr = ','.join (sub_checkpoint_list)
    if project.id == constant.competition_project_id:
        columstr = columstr.replace(',B12,', ',S1,')
        columstr = columstr.replace(',B14a,', ',S2,')
        columstr = columstr.replace(',D32,', ',S3,')
        columstr = columstr.replace(',D33,', ',S4,')
        columstr = columstr.replace(',D41a,', ',S5,')
        columstr = columstr.replace(',D40a,', ',S6,')
    elif project.id == constant.current_mini_project_id:
        columstr = columstr.replace(',D63,', ',T1,')
        columstr = columstr.replace(',D40a,', ',T2,')
        columstr = columstr.replace(',G51,', ',T3,')
        
    sql = 'select %s from mc_reportdata where id=%s;' % (columstr, report_id)
    try:
        c, con = DbUtils.cursor()
        c.execute(sql)
        cur = c.fetchone()
    finally:
        if c:
            c.close()
        if con:
            con.close() 
    return cur

def get_otherreport_group_score_0(report_id, cp_group_list_str):
    sql = 'select %s from mc_otherreportdata where id=%s;' % (cp_group_list_str, report_id)
    try:
        c, con = DbUtils.cursor()
        c.execute(sql)
        ret = c.fetchone()
    finally:
        if c:
            c.close()
        if con:
            con.close() 
    if ret:
        return [score or 0 for score in ret]
    
    return None

def get_otherreport_sub_score(report_id, project_id):
    sql = 'select %s from mc_otherreportdata where id=%s;' % (get_sub_score_column_str(project_id), report_id)
    try:
        c, con = DbUtils.cursor()
        c.execute(sql)
        cur = c.fetchone()
    finally:
        if c:
            c.close()
        if con:
            con.close() 
    return cur

#MAIN_SCORE_COLUMN_STR = None
def get_main_score_column_str(project):
    MAIN_SCORE_COLUMN_STR = None
    if not MAIN_SCORE_COLUMN_STR:
        field_list = ['total']
        field_list.extend([cp.name for cp in _checkpoint.get_project_cp_list(project)])
        MAIN_SCORE_COLUMN_STR = ','.join(field_list)
    return MAIN_SCORE_COLUMN_STR

def get_main_group_score_column_str(project, has_min_max=False):
    MAIN_GROUP_SCORE_COLUMN_STR = None
    if not MAIN_GROUP_SCORE_COLUMN_STR:
        MAIN_GROUP_SCORE_COLUMN_STR = [cp for cp in _checkpoint.get_project_cp_group_list(project.id)]
    return MAIN_GROUP_SCORE_COLUMN_STR

def get_sub_score_column_str(project_id):
    SUB_SCORE_COLUMN_STR = None
    if not SUB_SCORE_COLUMN_STR:
        SUB_SCORE_COLUMN_STR = ','.join([cp.name for cp in _checkpoint.get_sub_checkpoint_list(project_id)])
    return SUB_SCORE_COLUMN_STR

def get_bmw_top_score(term, report, checkpoint=None):
    column = checkpoint.name if checkpoint else 'total'
    term_id = term.id
    dealertype_id = report.dealer.dealertype.id
    sql = 'select max(data.%(column)s) from mc_report r,mc_reportdata data where r.term_id=%(term_id)s and r.id=data.id and r.dealertype_id=%(dealertype_id)s;' % vars()
    try:
        c, con = DbUtils.cursor()
        c.execute(sql)
        cur = c.fetchone()
    finally:
        if c:
            c.close()
        if con:
            con.close() 
    return cur[0]

DEALERTYPE_BMW = None
def get_dealertype_BMW():
    global DEALERTYPE_BMW
    if DEALERTYPE_BMW is None:
        DEALERTYPE_BMW = DealerType.objects.get(name_en='BMW')
    return DEALERTYPE_BMW

DEALERTYPE_MINI = None
def get_dealertype_MINI():
    global DEALERTYPE_MINI
    if DEALERTYPE_MINI is None:
        DEALERTYPE_MINI = DealerType.objects.get(name_en='MINI')
    return DEALERTYPE_MINI
    

@commit_on_success
def generate_report_by_paper(papers):
    u"""更新指定dealer的report数据"""
    project_dict = {} #同种类型的问卷字典分
    for p in papers:
        project = p.project
        paper_list = project_dict.get(project)
        if paper_list is None:
            paper_list = []
        paper_list.append(p)
        project_dict[project] = paper_list
    try:
        c, con = DbUtils.cursor()
        for project in project_dict.keys():
            papers = project_dict.get(project)
            gen_papers_score(project, papers, c, con)
    finally:
        if c:
            c.close()
        if con:
            con.close() 
    set_dirty()

def gen_papers_score(project, papers, c, con):
    if papers is None or len(papers) < 1:
        return
    valid_status = enums.PAPER_STATUS_FINISH #审核结束, 供sql调用
    #该project下检查点的选项(id,得分)字典
    cp_alt_score_dict = _alternative.get_project_cp_alt_score_dict(project)
    #survey_respondentdata的字�
    resp_column_list = _checkpoint.get_project_paper_resp_col_list(project)
    resp_column_str = ','.join(resp_column_list)#供sql调用
    #该project下统计A－F计分
    paper_ids_str = ','.join([str(p.id) for p in papers]) #供sql调用
    #report列字�
    report_column_cp_list = _checkpoint.get_project_sub_cp_list(project)
    #获得一类project下，审核的papers的算分题答案
    sql = "select paper.id,%(resp_column_str)s  from survey_respondent resp, survey_respondentdata data, mc_paper paper  where data.id = resp.id and paper.respondent_id=resp.id and paper.status>=%(valid_status)s and paper.id in (%(paper_ids_str)s)" % vars()
    c.execute(sql)
    results = c.fetchall()
    #生成pid,paper字典供取paper
    paper_dict = dict([(p.id, p)    for p in papers])
    for data in results:
        paper = paper_dict[int(data[0])]
        respond_column_data = data[1:]
        #根据列选择的alt的id值，从alt_score字典中，生成respond列的得分数组, 会有'null'�
        #最�题是G环节，打分题,最终得分就是实际得分，最�题不计分
        #以下只要更新mc_reportdata相应的得分列, 未填也作null更新
        u'''resp_score_list 得分，与 resp_column_list 是survey_respondentdata一一对应的，
        report_column_list,resp_column_list 也是对应的，只是列名可能会有差异'''
        paper_score_dict = {}
        cal_cp_list = []#有效的检查点list
        
        for tmpindex, cp in  enumerate(report_column_cp_list):
            value = respond_column_data[tmpindex] #respondent_data，列有� 此值为alternative_id
            if value is None or value == '':
                continue
            alternative = []
            if isinstance(value, (int, long, float)):
                alternative = Alternative.objects.filter(id=value, question=cp.question)
            #打分题特殊处理（老题号G51，新题号G50--即name_abbr）
            if cp.name == 'G51':
                cal_cp_list.append(cp)
            elif len(alternative) > 0:
                #剔除选择'不适用'的检查点
                if alternative[0].cid == 'A3':
                    paper_score_dict[cp.name] = 'null'
                    continue
                cal_cp_list.append(cp)
            if cp.name == 'G51':
                #G51打分题目
                paper_score_dict[cp.name] = value
            else:
                paper_score_dict[cp.name] = map_score(value, cp_alt_score_dict)
            if cp.name == 'T3':
                    paper_score_dict[cp.name] = '"%s"' % value
                
        #生成环节及检查点结构
        cp_group_id_map = {}
        for cp in cal_cp_list:
            grp = cp_group_id_map.get(cp.parent.id, None)
            if grp is None:
                grp = cp.parent
                grp.child_lists = []
                cp_group_id_map[cp.parent.id] = grp
            grp.child_lists.append(cp)
        #计算环节�
        checkpoint_group = get_avg_for_checkpoint_group(paper, paper_score_dict, cp_group_id_map.values())
        paper_score_dict.update(checkpoint_group) 
        update_one_project_papers_report(paper, paper_score_dict, c, con) #生成report及report_data,更新paper.score
        

def calculate_paper_total_score(paper):
    #该project下检查点的选项(id,得分)字典
    cp_alt_score_dict = _alternative.get_project_cp_alt_score_dict(paper.project)
    #样卷答案字典，以resp_col为key
    respond_dict = survey_utils.get_respondentdata_dict_by_paper(paper)
    print respond_dict
    sub_cp_list = _checkpoint.get_project_sub_cp_list(paper.project)
    paper_score_dict = {}
    cp_group_id_map = {}
    cal_cp_list = []  #有效检查点
    for cp in sub_cp_list:
        value = respond_dict.get(cp.resp_col) #respondent_data，列有� 此值为alternative_id
        if value is None or value == '':
            continue
        alternative = []
        if isinstance(value, (int, long, float)):
            alternative = Alternative.objects.filter(id=value, question=cp.question)
        #打分题特殊处理（老题号G51，新题号G50--即name_abbr）
        if cp.name == 'G51':
            cal_cp_list.append(cp)
        elif len(alternative) > 0:
            #剔除选择'不适用'的检查点
            if alternative[0].cid == 'A3':
                paper_score_dict[cp.name] = 'null'
                continue
            cal_cp_list.append(cp)
        if cp.name == 'G51':
            #G51打分题目
            paper_score_dict[cp.name] = value
        else:
            paper_score_dict[cp.name] = map_score(value, cp_alt_score_dict)
        if cp.name == 'T3':
                paper_score_dict[cp.name] = '"%s"' % value
    #生成环节及检查点结构
    for cp in cal_cp_list:
        grp = cp_group_id_map.get(cp.parent.id, None)
        if grp is None:
            grp = cp.parent
            grp.child_lists = []
            cp_group_id_map[cp.parent.id] = grp
        grp.child_lists.append(cp)
    checkpoint_group = get_avg_for_checkpoint_group(paper, paper_score_dict, cp_group_id_map.values())
    paper_score_dict.update(checkpoint_group) 
    paper.score = checkpoint_group.get('total')
    try:
        c, con = DbUtils.cursor()
        update_one_project_papers_report(paper, paper_score_dict, c, con, True) #生成report及report_data,更新paper.score
    finally:
        if c:
            c.close()
        if con:
            con.close() 
            
def update_one_project_papers_report(paper, paper_score_dict, c, con, only_update=False):
    report = None
    try:
        reports = Report.objects.filter(respondent__id=paper.respondent.id)
        if reports and len(reports) > 0:
            report = reports[0]
    except Report.DoesNotExist, ex:
        print ex
        pass
    
    if report is None:
        #在批量保存时，若无report则直接返回
        if only_update:
            return
        report = Report()
        report.respondent_id = paper.respondent.id
        report.dealer_id = paper.dealer.id
        report.dealer_name = paper.dealer.name
        report.dealertype_id = paper.dealer.dealertype.id
        report.term_id = paper.term.id
        report.term_name = paper.term.name
        report.paper_type = paper.paper_type
        report.project = paper.project
        report.save()
        
    select_reportdt_sql = 'select id from mc_reportdata where id = %s' % str(report.id)
    c.execute(select_reportdt_sql)
    datafound = c.fetchone()
    if datafound is None or len(datafound) == 0:
        #新建的report，主动插入条reportdata,仅有id, 以下全只要更新列�
        insert_reportdt_sql = 'insert into mc_reportdata (id) values(%s)' % str(report.id)
        c.execute(insert_reportdt_sql)
        if con:
            con.commit()
    
    
    sql_str = ','.join(['%s=%%(%s)s' % (key, key) for key in paper_score_dict])
    sql = "update mc_reportdata set %s where id=%s" % (sql_str, report.id)    
    sql = sql % paper_score_dict
    c.execute(sql)
    if con:
        con.commit()
    total_score = paper_score_dict['total']
    report.score = total_score
    report.paper_type = paper.paper_type
    report.project = paper.project
    report.save()
    
    paper.score = total_score
    paper.save()

    
def get_avg_for_checkpoint_group(paper, score_dict, cp_group_list=None):
    u''' 若某环节都没有填，就不用放入字典，选择‘不适用’的题目不作统计, 
        cp_group_list为环节点，且有child_list，此child_list排除了选择‘不适用’选项 '''
    result = {}
    total_numb = 0
    total_score = 0 
    if cp_group_list is None:
        cp_group_list = _checkpoint.get_project_cp_group_list(paper.project.id)
    
    for cp_group in cp_group_list:
        group_score_list = []
        part_total = 0
        cp_lists = cp_group.child_lists or cp_group.child_list
        size = len(cp_lists) #剔除“不适用”题目
        for child_cp in cp_lists:
            #宝马问卷的G64题不计入G部分算分
            if child_cp.name == 'G64':
                size -= 1
                continue
            score = score_dict.get(child_cp.name)
            if score is not None and score != 'null':
                group_score_list.append(score)
        if  len(group_score_list) > 0:
            part_total = sum(group_score_list)
            result[cp_group.name] = float(part_total) / size
        else:
            result[cp_group.name] = 'null'
        result['%s_COUNT' % cp_group.name] = size
        result['%s_SUM' % cp_group.name] = float(part_total) 
        #G环节，不参与总分的计算，倒数第二题为打分�
        if cp_group.name != 'G':
            total_numb += len(cp_lists)
            total_score += part_total
    total = 0
    if total_numb:
        total = float(total_score) / total_numb
    result['total'] = total
    return result

def map_score(x, cp_alt_score_dict):
    '''返回null，是为了mc_reportdata全列字段填充，以保证如果上次有数据，而本次操作未更到的字段，也会清空 '''
    if x:
        if isinstance(x, (int, long, float)):
            ret = cp_alt_score_dict.get(int(x), 'null')
            if ret is None:
                ret = 'null'
            return ret
    return 'null'

def aggregate_otherreport(term=None):
    '''生成访问员、进店人数、新店和老店的统计分数'''
    dealer_types = _dealer.get_dealer_types()
    if term:
        term_list = [term]
    else:
        term_list = _term.get_2012_all_terms()
    #访问员分数统计
    aggregate_user_otherreport(dealer_types, term_list)
    #进店人数分数统计
    aggregate_num_otherreport(dealer_types, term_list)
    #新店和老店分数统计
    dealer_types = dealer_types.filter(name_en='BMW')
    aggregate_newold_otherreport(dealer_types, term_list)
    
def aggregate_user_otherreport(dealer_types, term_list):
    users = list(_user.getUsers())
    for u in users:
        if 'gfk' in u.username:
            users.remove(u)
    for term in term_list:
        for dealer_type in dealer_types:
            save_otherreport('user', users, term, dealer_type)
    return
def aggregate_num_otherreport(dealer_types, term_list):
    for term in term_list:
        for dealer_type in dealer_types:
            papers = _paper.get_papers(dealer__dealertype__id=dealer_type.id, term=term)
            visitor_list = []
            for paper in papers:
                visitor_list.append(paper.visitor_num)
            visitor_list = list(set(visitor_list))
            save_otherreport('num', visitor_list, term, dealer_type)
    return
def aggregate_newold_otherreport(dealer_types, term_list):
    for term in term_list:
        for dealer_type in dealer_types:
            new_old = ['new', 'old']
            save_otherreport('newold', new_old, term, dealer_type)
    return

#保存数据，同步将数据插入或更新otherreport表和otherreportdata表
def save_otherreport(kind, search_list, term, stype):
    project_id = constant.dealertype_id_to_project_id(stype.id)
    items = _paper.get_papers_info(term, project_id, search_list, stype)
    project = _project.get_project_by_id(project_id)
    other_report = None
    create = False
    if kind == 'user':
        for item in items:
            other_report, create = OtherReport.objects.get_or_create(user=item.search_item, report_type=kind, term=term, dealertype=stype)
            other_report.dealer_num = item.dealer_num
            other_report.max_score = item.max_score
            other_report.min_score = item.min_score
            other_report.ave_score = item.ave_score
            other_report.save()
            save_item(item, project, term, other_report, create)
    if kind == 'num':
        for item in items:
            other_report, create = OtherReport.objects.get_or_create(visitor_num=item.search_item, report_type=kind, term=term, dealertype=stype)
            other_report.dealer_num = item.dealer_num
            other_report.max_score = item.max_score
            other_report.min_score = item.min_score
            other_report.ave_score = item.ave_score
            other_report.save()
            save_item(item, project, term, other_report, create)
    if kind == 'newold':
        for item in items:
            is_new = False
            if 'new' in item.search_item:
                is_new = True
            other_report, create = OtherReport.objects.get_or_create(newold=is_new, report_type=kind, term=term, dealertype=stype)
            other_report.dealer_num = item.dealer_num
            other_report.max_score = item.max_score
            other_report.min_score = item.min_score
            other_report.ave_score = item.ave_score
            other_report.save()
            save_item(item, project, term, other_report, create)
            
def save_item(item, project, term, other_report, create):
    if other_report:
        resp_id_list = []
        if item.papers:
            for paper in item.papers:
                if paper.respondent:
                    resp_id_list.append(paper.respondent.id)
                else:
                    print 'no responded: paper=%d, dealer=%d' % (paper.id, paper.dealer.id)
        aggreate_otherreportdata(resp_id_list, project, term, other_report, create)

@commit_on_success
def aggreate_otherreportdata(resp_id_list, project, term, other_report, create):
    total_cp_name_list = _checkpoint.get_project_cp_name_list_with_total(project, False)
    #total_cp_name_list_str = ','.join(total_cp_name_list)
    cp_avg_list_str = ','.join(['avg(%s)' % name for name in total_cp_name_list])
    resp_id_list_str = ','.join(map(str, resp_id_list))
    project_id = project.id
    paper_type = enums.BMW_PAPER_TYPE
    if project.id == constant.competition_project_id:
        paper_type = enums.FW_PAPER_TYPE
    try:
        c, con = DbUtils.cursor()
        term_id = term.id
        
        #只取bmw终审得分或竞品取fw问卷
        sql = 'select min(total), max(total), %(cp_avg_list_str)s from mc_reportdata data,mc_report report where report.project_id=%(project_id)s and report.paper_type=\'%(paper_type)s\' and report.term_id=%(term_id)s and data.id=report.id and report.respondent_id in (%(resp_id_list_str)s);' % vars()
        c.execute(sql)
        data_list = c.fetchone()
        score_list = map(handle_sql_data, data_list)
        paper_score_dict = {}
    #    paper_score_dict['min_total'] = score_list[0]
    #    paper_score_dict['max_total'] = score_list[1]
        for i, score in enumerate(score_list[2:]):
            paper_score_dict[total_cp_name_list[i]] = score
        if term.is_finished():
            if create:
                #新建的otherreport，主动插入条mc_otherreportdata,仅有id, 以下全只要更新列
                insert_reportdt_sql = 'insert into mc_otherreportdata (id) values(%s)' % str(other_report.id)
                c.execute(insert_reportdt_sql)
                if con:
                    con.commit()
            #print u'%d-%d-%s: %s >> %s' % (dealer.id, dealer.level, dealertype.name_en, report.score, dealer_id_list_str)
            sql_str = ','.join(['%s=%%(%s)s' % (key, key) for key in paper_score_dict])
            sql = "update mc_otherreportdata set %s where id=%s" % (sql_str, other_report.id)    
            sql = sql % paper_score_dict
            c.execute(sql)
            if con:
                con.commit()
        else:
            #print u'%s 尚未结束, 不予统计平均� % term.name
            pass
    finally:
            if c:
                c.close()
            if con:
                con.close() 


def aggregate_report(dealer=None, level=0):
    
    '''因为递归深度有限，拆分一类一类统计'''
    print u'===orignal dealer groupd type ===='
    aggregate_jt_report(dealer, level)
    print u'===sub district dealer type ===='
    aggregate_xq_report(dealer, level)
    print u'===province dealer type ===='
    aggregate_province_report(dealer, level)
    print u'===orignal dealer type ===='
    aggregate_orignal_report(dealer, level)
    #print u'===brand dealer type ===='
    #aggregate_brand_report(dealer, level)
    return
@commit_on_success
def aggregate_xq_report(dealer=None, level=0):
    """自底向上统计小区平均� 应该只统计BMW类型的paper得分
    Book.objects.aggregate(Avg('price'))
    {'price__avg': 34.35}    
    """
    if not dealer:
        dealer = Dealer.objects.get(parent=None)
    if not dealer.has_child: return
    child_list = Dealer.objects.filter(xq_parent=dealer)
    if not child_list: return
    
    for child in child_list:
        if child.has_child:
            level += 1
            aggregate_xq_report(child, level)
            level -= 1
            #在速度慢的电脑,会出现sqlite数据库无法打开的错�这里降低速度,回避这个问题
            time.sleep(0.1)
        else:
            break
    aggreate_dealer_projects_terms_report(dealer, level, False)
    return
@commit_on_success
def aggregate_jt_report(dealer=None, level=0):
    """自底向上统计集团平均� 应该只统计BMW类型的paper得分
    """
    if not dealer:
        dealer = Dealer.objects.get(parent=None)
    if not dealer.has_child: return
    child_list = Dealer.objects.filter(jt_parent=dealer)
    if not child_list: return
    
    for child in child_list:
        if child.has_child:
            level += 1
            aggregate_jt_report(child, level)
            level -= 1
            #在速度慢的电脑,会出现sqlite数据库无法打开的错�这里降低速度,回避这个问题
            time.sleep(0.1)
        else:
            break
    aggreate_dealer_projects_terms_report(dealer, level, False)
    return
@commit_on_success
def aggregate_province_report(dealer=None, level=0):
    """自底向上统计省份平均� 应该只统计BMW类型的paper得分
    Book.objects.aggregate(Avg('price'))
    {'price__avg': 34.35}    
    """
    if not dealer:
        dealer = Dealer.objects.get(parent=None)
    if not dealer.has_child: return
    child_list = Dealer.objects.filter(sf_parent=dealer)
    if not child_list: return
    
    for child in child_list:
        if child.has_child:
            level += 1
            aggregate_province_report(child, level)
            level -= 1
            #在速度慢的电脑,会出现sqlite数据库无法打开的错�这里降低速度,回避这个问题
            time.sleep(0.1)
        else:
            break
    aggreate_dealer_projects_terms_report(dealer, level)
    return

@commit_on_success
def aggregate_brand_report(dealer=None, level=0):
    """自底向上统计省份平均� 应该只统计BMW类型的paper得分
    Book.objects.aggregate(Avg('price'))
    {'price__avg': 34.35}    
    """
    if not dealer:
        dealer = Dealer.objects.get(parent=None)
    if not dealer.has_child: return
    child_list = Dealer.objects.filter(dt_parent=dealer)
    if not child_list: return
    
    for child in child_list:
        if child.has_child:
            level += 1
            aggregate_brand_report(child, level)
            level -= 1
            #在速度慢的电脑,会出现sqlite数据库无法打开的错�这里降低速度,回避这个问题
            time.sleep(0.1)
        else:
            break
    aggreate_dealer_projects_terms_report(dealer, level)
    return
@commit_on_success
#生成原始区域、城市统计得�
def aggregate_orignal_report(dealer=None, level=0):
    """自底向上统计平均� 应该只统计BMW类型的paper得分
    Book.objects.aggregate(Avg('price'))
    {'price__avg': 34.35}    
    """
    if not dealer:
        dealer = Dealer.objects.get(parent=None)
    if not dealer.has_child: return
    child_list = Dealer.objects.filter(parent=dealer)
    if not child_list: return
    
    for child in child_list:
        if child.has_child:
            level += 1
            aggregate_orignal_report(child, level)
            level -= 1
            #在速度慢的电脑,会出现sqlite数据库无法打开的错�这里降低速度,回避这个问题
            time.sleep(0.1)
        else:
            break
    aggreate_dealer_projects_terms_report(dealer, level)
    return

def aggreate_dealer_projects_terms_report(dealer, level, check=False):
    '''
    check 表示2011年无数据 
    '''
    #所有的平均分都是下属单店分数的平均� 而不是直属子节点的分数的平均�
    sub_leaf_dealer_list = _dealer.get_sub_leaf_dealer_list(dealer)
    #该条report为总体平均分，
#    report = Report.objects.get_or_create(dealer=dealer, term=None)[0]
#    if dealer.name_en:
#        report.dealer_name = '%s%s/%s' % (u'　' * level, dealer.name, dealer.name_en)
#    else:
#        report.dealer_name = '%s%s' % (u'　' * level, dealer.name)
#    report.save()
    
    term_list = _term.get_2012_all_terms()
    
        
    #按品牌统�
    dealer_type_map = {}
    for subd in sub_leaf_dealer_list:
        sub_dealer_list = dealer_type_map.get(subd.dealertype, None)
        if sub_dealer_list is None:
            sub_dealer_list = []
            dealer_type_map[subd.dealertype] = sub_dealer_list
        sub_dealer_list.append(subd)
    
#    #统计2011年指定问卷，或是3个问卷模板的区域，省份，集团，小区平均得�
#    project_2011 = Project.objects.get(id=1);
#    terms_2011 = Term.objects.filter(id__lt=5)
#    for dt  in dealer_type_map.keys():
#        sub_dealer_list = dealer_type_map.get(dt)
#        aggreate_dealer_projects_terms_report_0(dealer, level, dt, sub_dealer_list, project_2011, terms_2011, check)
            
    #统计2012年指定问卷，或是3个问卷模板的区域，省份，集团，小区平均得�
    for dt  in dealer_type_map.keys():
        sub_dealer_list = dealer_type_map.get(dt)
        project_id = constant.dealertype_id_to_project_id(dt.id)
        pro = _project.get_project_by_id(project_id)
        aggreate_dealer_projects_terms_report_0(dealer, level, dt, sub_dealer_list, pro, term_list, False)
        
def aggreate_dealer_projects_terms_report_0(dealer, level, dealertype, sub_leaf_dealer_list, project, term_list, check=False):
        total_cp_name_list = _checkpoint.get_project_cp_name_list_with_total(project)
        dealer_id_list_str = ','.join([str(d.id) for d in sub_leaf_dealer_list])
        #total_cp_name_list_str = ','.join(total_cp_name_list)
        cp_avg_list_str = ','.join(['avg(%s)' % name for name in total_cp_name_list])
        
        paper_type = enums.BMW_PAPER_TYPE
        if project.id == constant.competition_project_id or project.id == constant.old_project_id:
            paper_type = enums.FW_PAPER_TYPE
        project_id = project.id
        items = ['min(total)', 'max(total)'
                        , '(ifnull(sum(A_SUM),0)+ifnull(sum(B_SUM),0)+ifnull(sum(C_SUM),0)+ifnull(sum(D_SUM),0)+ifnull(sum(E_SUM),0)+ifnull(sum(F_SUM),0))/(ifnull(sum(A_COUNT),0)+ifnull(sum(B_COUNT),0)+ifnull(sum(C_COUNT),0)+ifnull(sum(D_COUNT),0)+ifnull(sum(E_COUNT),0)+ifnull(sum(F_COUNT),0))'
                        , 'sum(A_SUM)/sum(A_COUNT)', 'sum(B_SUM)/sum(B_COUNT)', 'sum(C_SUM)/sum(C_COUNT)'
                        , 'sum(D_SUM)/sum(D_COUNT)', 'sum(E_SUM)/sum(E_COUNT)', 'sum(F_SUM)/sum(F_COUNT)'
                        ]
        itemstrs = ','.join(items)
        sqlstr = '%s,%s' % (itemstrs, cp_avg_list_str)
        try:
            c, con = DbUtils.cursor()
            for term in term_list:
    #            print term.name_cn, dealer.name
                if not term.is_finished:
                    continue
                term_id = term.id
                #只取bmw终审得分或竞品取fw问卷
                sql = 'select %(sqlstr)s from mc_reportdata data,mc_report report where report.project_id=%(project_id)s and report.term_id=%(term_id)s and data.id=report.id and report.dealer_id in (%(dealer_id_list_str)s);' % vars()
                print  'Query: ', sql
                c.execute(sql)
                
                data_list = c.fetchone()
                score_list = map(handle_sql_data, data_list)
                paper_score_dict = {}
                paper_score_dict['min_total'] = score_list[0]
                paper_score_dict['max_total'] = score_list[1]
                for i, score in enumerate(score_list[9:]):
                    paper_score_dict[total_cp_name_list[ i]] = score
                    if check:
                        paper_score_dict[total_cp_name_list[ i]] = 'null'
                
                if project.id == 1:
                    paper_score_dict['A'] = 'null'
                    paper_score_dict['B'] = 'null'
                    paper_score_dict['C'] = 'null'
                    paper_score_dict['D'] = 'null'
                    paper_score_dict['E'] = 'null'
                    paper_score_dict['F'] = 'null'
                    paper_score_dict['G'] = 'null'
                else:
                    #仅大区 仅BMW,MINI按有效题算,其他求和平均
                    if dealer.level <= 1 :
                        national_jingpin = dealer.level == 0 and project.id == 4
                        if dealertype.id == 1 or dealertype.id == 5 or national_jingpin:
                            paper_score_dict['total'] = score_list[2]
                            paper_score_dict['A'] = score_list[3]
                            paper_score_dict['B'] = score_list[4]
                            paper_score_dict['C'] = score_list[5]
                            paper_score_dict['D'] = score_list[6]
                            paper_score_dict['E'] = score_list[7]
                            paper_score_dict['F'] = score_list[8]
                        
                    
                report, reportCreated = Report.objects.get_or_create(dealer=dealer, term=term, dealertype=dealertype, project=project)
                if dealer.name_en:
                    report.dealer_name = ' %s %s /%s %s %s' % (u'　' * level, dealer.name, dealer.name_en, term.name, dealertype.name_cn)
                else:
                    report.dealer_name = ' %s %s %s %s' % (u'　' * level, dealer.name, term.name, dealertype.name_cn)
                report.term_name = term.name
                tscore = paper_score_dict.get('total', None)
                if tscore == 'null':
                    report.score = None
                else:
                    report.score = tscore
                    
                report.project = project
                report.paper_type = paper_type
                report.save()
                if term.is_finished():
                    if reportCreated:
                        #新建的report，主动插入条reportdata,仅有id, 以下全只要更新列�
                        insert_reportdt_sql = 'insert into mc_reportdata (id) values(% s)' % str(report.id)
                        c.execute(insert_reportdt_sql)
                        if con:
                            con.commit()
                    print u'r: %d = p: %d - t: %d - d: %d -%s -%d -%s: %s >> %s' % (report.id, project.id, term.id, dealer.id, paper_type, dealer.level, dealertype.name_en, report.score, dealer_id_list_str)
                   
    #                sql_str = ', '.join([' % s = %% (% s)s' % (key, key) for key in paper_score_dict])
    #                sql = "update mc_reportdata set %s where id=%s" % (sql_str, report.id)    
    #                print "TMP: %s " % sql
    #                sql = sql % paper_score_dict
    #                print 'Update:%s ' % sql
    #                c.execute(sql)
                    partly_update(report.id, paper_score_dict, c, con)
                else:
                    #print u' % s 尚未结束, 不予统计平均� % term.name
                    pass
        finally:
            if c:
                c.close()
            if con:
                con.close() 

def partly_update(reportid, paper_score_dict, c, con, update_fields=20):
    #全列值更新，需要测试null值字段是否存在
    size = len(paper_score_dict)
    lefts = size % update_fields
    times = size / update_fields
    if lefts:
        times += 1
    key_list = paper_score_dict.keys()
    for i in  range(0, times):
        part_dict = {}
        start = i * update_fields
        end = start + update_fields
        part_keys = key_list[start: end]
        for key in part_keys:
            val = paper_score_dict.get(key, 'null') 
            paper_score_dict.pop(key, 0)
            if  isinstance(val, str)  or isinstance(val, unicode) :
                if val != 'null':
                    val = '"%s"' % val
            part_dict[key] = val
        sql_str = ','.join(['%s=%%(%s)s' % (key, key) for key in part_dict])
        sql = "update mc_reportdata set %s where id=%s" % (sql_str, reportid)
        sql = sql % part_dict
        print 'part %s: %s' % (i, sql)
        c.execute(sql)
        if con:
            con.commit()
        
        
def handle_sql_data(data):
    if data is None:
        return 'null'
    return str('%0.15g' % data)

def get_reportdata_by_paper(paper):
    cp_list = _checkpoint.get_checkpoint_list_by_project(paper.project)
    cp_str_list = ','.join([str(cp.name) for cp in cp_list])
    report = Report.objects.filter(respondent=paper.respondent)[0]
    if report:
        report_id = '%s' % report.id
        sql = 'select %(cp_str_list)s from mc_reportdata where id = %(report_id)s;' % vars()
        try:
            c, con = DbUtils.cursor()
            c.execute(sql)
            cp_score_list = c.fetchone()
        finally:
            if c:
                c.close()
            if con:
                con.close() 
        results = []
        for cp_score in cp_score_list:
            if cp_score:
                results.append(cp_score)
            else:
                results.append(u'不适用')
        return results
    else:
        return None

cp_group_term_score_dict = {}
def get_cp_group_term_score(dealer, term, checkpoint, paper, column_list=None):
    if dealer is None:
        return None
    key = (dealer.id, term.id)
    score_list = cp_group_term_score_dict.get(key)
    if score_list is None:
        score_list = get_dealer_score(term, dealer, paper.project, paper.dealer.dealertype, paper.paper_type, column_list)
        cp_group_term_score_dict[key] = score_list
    
    if score_list is None:
        return 0
    
    return score_list[checkpoint.index]

def get_cp_child_term_score(dealer, term, checkpoint, paper):
    score_list = get_dealer_sub_score(term, dealer, paper.project, paper.dealer.dealertype, paper.paper_type)
    if score_list is None:
        return 0
    
    sub_cp_index_dict = _checkpoint.get_sub_cp_index_dict(paper.project.id)
    return score_list[sub_cp_index_dict.get(checkpoint.id)]


#根据paper获得经销商数�
def get_dealer_data(paper):
    
    if not paper:
        #尚未录入问卷
        return {}
    
    #经销�
    dealer = paper.dealer
    curr_term = paper.term
    project_id = paper.project.id
    cp_list = _checkpoint.get_checkpoint_group_list_with_total(project_id)
    question_list = _checkpoint.get_project_sub_cp_list(paper.project)
    term_list = list(_term.get_2012_all_terms().filter(id__lte=curr_term.id))
    if curr_term == None:        
        curr_term = term_list[-1]
    
    #全国
    dealer_nation = _dealer.get_dealer_parent_by_level(dealer, constant.LEVEL_NATION)
    #大区
    dealer_daqu = _dealer.get_dealer_parent_by_level(dealer, constant.LEVEL_DAQU)
    #小区
    dealer_xq = _dealer.get_dealer_parent_by_level(dealer, constant.LEVEL_XQ)
    #省份
    dealer_province = _dealer.get_dealer_parent_by_level(dealer, constant.LEVEL_PROVINCE)
    #城市
    dealer_city = _dealer.get_dealer_parent_by_level(dealer, constant.LEVEL_CITY)
    #经销商集�
    dealer_jt = _dealer.get_dealer_parent_by_level(dealer, constant.LEVEL_JT)
    
    cp_group_list = map(copy.copy, _checkpoint.get_checkpoint_group_list_with_total(project_id))
    cp_name_list = [cp.name for cp in cp_group_list]
    
    for cp in cp_list:
        cp.score_list = []
        cp.score_list_nation = []
        cp.score_list_daqu = []
        cp.score_list_xq = []
        cp.score_list_province = []
        cp.score_list_city = []
        cp.score_list_jt = []
        cp.score_list_top = []
        for i in range(4):
            if i < len(term_list):
                score = get_cp_group_term_score(dealer, term_list[i], cp, paper, cp_name_list)
                score_nation = get_cp_group_term_score(dealer_nation, term_list[i], cp, paper, cp_name_list)
                score_daqu = get_cp_group_term_score(dealer_daqu, term_list[i], cp, paper, cp_name_list)
                score_xq = get_cp_group_term_score(dealer_xq, term_list[i], cp, paper, cp_name_list)
                score_province = get_cp_group_term_score(dealer_province, term_list[i], cp, paper, cp_name_list)
                score_city = get_cp_group_term_score(dealer_city, term_list[i], cp, paper, cp_name_list)
                score_jt = get_cp_group_term_score(dealer_jt, term_list[i], cp, paper, cp_name_list)
                score_top = get_bmw_top_score(term_list[i], paper, cp)
            else:
                score = ''
                score_nation = ''
                score_daqu = ''
                score_xq = ''
                score_province = ''
                score_city = ''
                score_jt = ''
                score_top = ''
            #暂时都为空
            score_nation = ''
            score_daqu = ''
            score_xq = ''
            score_province = ''
            score_city = ''
            score_jt = ''
            score_top = ''
            if i + 1 == curr_term.id:
                curr_term.score = score_nation
            cp.score_list.append('%.1f' % score if score else '')
            cp.score_list_nation.append('%.1f' % score_nation if score_nation else '')
            cp.score_list_daqu.append('%.1f' % score_daqu if score_daqu else '')
            cp.score_list_xq.append('%.1f' % score_xq if score_xq else '')
            cp.score_list_province.append('%.1f' % score_province if score_province else '')
            cp.score_list_city.append('%.1f' % score_city if score_city else '')
            cp.score_list_jt.append('%.1f' % score_jt if score_jt else '')
            cp.score_list_top.append('%.1f' % score_top if score_top else '')
        
        cp.sub_cp_list = []
        for sub_cp in cp.child_list:
            sub_cp.score_list = []
            for i in range(4):
                if i < len(term_list) and sub_cp.name != 'T3':
                    score = get_cp_child_term_score(dealer, term_list[i], sub_cp, paper)
                    sub_cp.score_list.append('%.1f' % score if score is not None else u'不适用')
                else:
                    score = '-'
                    sub_cp.score_list.append(score)
            
            score = get_cp_child_term_score(dealer, curr_term, sub_cp, paper)
            sub_cp.zero_reason = ''
            sub_cp.zero_reason_en = ''
            if not score:
                sub_cp.zero_reason, sub_cp.zero_reason_en = _question.get_zero_reason(paper, sub_cp)
            cp.sub_cp_list.append(sub_cp)
    
    curr_term.score = cp_list[0].score_list[curr_term.id - 5]
    
    for cp in question_list:
        score = get_cp_child_term_score(dealer, curr_term, cp, paper)
        if cp.name != 'T3':
            cp.score = '%.1f' % score if score is not None else u'不适用'
        else:
            cp.score = '-'
        #~ print cp.name,score
        
        score_nation = get_cp_child_term_score(dealer_nation, curr_term, cp, paper)
        
        score_daqu = get_cp_child_term_score(dealer_daqu, curr_term, cp, paper)
        score_xq = get_cp_child_term_score(dealer_xq, curr_term, cp, paper)
        score_province = get_cp_child_term_score(dealer_province, curr_term, cp, paper)
        score_city = get_cp_child_term_score(dealer_city, curr_term, cp, paper)
        score_jt = get_cp_child_term_score(dealer_jt, curr_term, cp, paper)
        
        #暂时空
        score_nation = None
        score_daqu = None
        score_xq = None
        score_province = None
        score_city = None
        score_jt = None
        
        cp.score_nation = '%.1f' % score_nation if score_nation is not None else '-'
        cp.score_daqu = '%.1f' % score_daqu if score_daqu is not None else '-'
        cp.score_xq = '%.1f' % score_xq if score_xq is not None else '-'
        cp.score_province = '%.1f' % score_province if score_province is not None else '-'
        cp.score_city = '%.1f' % score_city if score_city is not None else '-'
        cp.score_jt = '%.1f' % score_jt if score_jt is not None else '-'
        
        if cp.score != '100.0':
            cp.zero_reason, cp.zero_reason_en = _question.get_zero_reason(paper, cp)
        else:
            cp.zero_reason, cp.zero_reason_en = '', ''
        
        if score is not None:
            if score_nation:
                nation_delta = score - score_nation
            else:
                nation_delta = 0
            cp.nation_delta = '%.1f' % nation_delta
            
            if score_daqu:
                daqu_delta = score - score_daqu
            else:
                daqu_delta = 0
            cp.daqu_delta = '%.1f' % daqu_delta
            
            if score_xq:
                xq_delta = score - score_xq
            else:
                xq_delta = 0
            cp.xq_delta = '%.1f' % xq_delta
            
            if score_province:
                province_delta = score - score_province
            else:
                province_delta = 0
            cp.province_delta = '%.1f' % province_delta
            
            if score_city:
                city_delta = score - score_city
            else:
                city_delta = 0
            cp.city_delta = '%.1f' % city_delta
            
            if score_jt:
                jt_delta = score - score_jt
            else:
                jt_delta = 0
            cp.jt_delta = '%.1f' % jt_delta
    
    respond = paper.respondent
    
    t3 = respond.get_data('T3')
    t3_result_en = paper.respondent.get_translation('T3')
    if t3 and t3_result_en:
        t3 += '<br>' + t3_result_en
                    
    #end
    bad_comments = respond.get_data('G50__A2')
    good_comments = respond.get_data('G50__A1')
    bad_comments_en = respond.get_translation('G50_A2')
    good_comments_en = respond.get_translation('G50_A1')
    score_comments = respond.get_data('G51__A1')
    
    repare_time = respond.get_data('repare_finish_time')
    estimate_time = respond.get_data('estimate_finish_time')
    
    begin_datetime = respond.visit_begin
    end_datetime = respond.visit_end
    visit_time = (end_datetime - begin_datetime).seconds / 60
    #print 'v',visit_time
    
    if respond.visit_begin:
        begin_time = respond.visit_begin.strftime('%H:%M')
    if respond.visit_end:
        end_time = respond.visit_end.strftime('%H:%M')
    
    return locals()

def get_otherreport(kind, term_id, dealertype_id):
    items = OtherReport.objects.filter(report_type=kind, term__id=term_id, dealertype__id=dealertype_id)
    return items
if __name__ == '__main__':
    aggregate_report()
#    aggregate_otherreport()
