#encoding:utf-8
from django.shortcuts import HttpResponseRedirect, Http404, HttpResponse
from django.contrib.auth.decorators import login_required
from core import _user, _term, _dealer, _paperaudit, _route, _question, _paper, _paperdiff, _checkpoint, _report
import constant 
from mc.models import PaperDiff, QuestionDiff
from survey.models import Alternative
from userpro import enums
from django.utils import simplejson
import DbUtils
from mc import enums as mcenums 

@login_required
def overview(request):
    current_term = _term.get_cur_input_term()
    
    dealertypes = _dealer.get_dealer_types()
    for dealertype in dealertypes:
        total = _dealer.get_dealer_count_by_dealertype(dealertype, current_term)
        if total == 0:
            done = remain = percent = 0
        else:    
            done = _dealer.get_dealertype_done_survey_count(dealertype, current_term)
            remain = total - done
            percent = float(done) * 100 / total
        dealertype.sum_data = dict(total=total, done=done, remain=remain, percent=percent)
    return locals()

@login_required
def reginal(request):
    current_term = _term.get_cur_input_term()
    
    region_list = list(_dealer.get_regionals())
    for region in region_list:
        total = _dealer.get_dealer_count_by_region(region, current_term)
        if total == 0:
            done = remain = percent = 0
        else:    
            done = _dealer.get_regional_done_survey_count(region, current_term)
            remain = total - done
            percent = float(done) * 100 / total
        region.sum_data = dict(total=total, done=done, remain=remain, percent=percent)
    return locals()

GFK_PERM_AUDITS = (
(enums.FW_INPUT_PERMISSION, 'fw_input', mcenums.FW_PAPER_STATUS_INIT),
(enums.FW_BEGIN_AUDIT_PERMISSION, 'qc1', mcenums.FW_PAPER_STATUS_WAIT_AUDIT_2),
(enums.FW_QC_AUDIT_PERMISSION, 'qc2', mcenums.FW_PAPER_STATUS_WAIT_AUDIT_3),
(enums.FW_QC_AUDIT_PERMISSION2, 'qc3', mcenums.FW_PAPER_STATUS_WAIT_AUDIT_4),
(enums.FW_AREA_AUDIT_PERMISSION, 'dd', mcenums.FW_PAPER_STATUS_WAIT_AUDIT_5),
(enums.FW_AUDIT_PERMISSION, 'yj', mcenums.FW_PAPER_STATUS_WAIT_AUDIT_6),
(enums.FW_END_AUDIT_PERMISSION, 'fw_end', mcenums.PAPER_STATUS_FINISH),
(enums.FH_INPUT_PERMISSION, 'fh_input', mcenums.FH_PAPER_STATUS_INPUT),
(enums.FH_END_AUDIT_PERMISSION, 'fh_end', mcenums.PAPER_STATUS_FINISH),
)
@login_required
def dealer(request):
    current_term = _term.get_cur_input_term()
    dealer_list = list(_dealer.get_leaf_dealer_for_bm(current_term))
    _dealer_status(current_term, [constant.current_project_id], dealer_list)
    column = 27
    return locals()

@login_required
def mini(request):
    current_term = _term.get_cur_input_term()
    dealer_list = list(_dealer.get_leaf_dealer_for_mini(current_term))
    _dealer_status(current_term, [constant.current_mini_project_id], dealer_list)
    column = 27
    return locals()

@login_required
def others(request):
    current_term = _term.get_cur_input_term()
    dealer_list = list(_dealer.get_leaf_dealer_other_than_bm(current_term))
    _dealer_status(current_term, [constant.competition_project_id], dealer_list, True)
    column = 22
    return locals()

#竞品
#def _com
#BMW/MINI
def _dealer_status(current_term, project_id_list, dealer_list, competition=False):
    diffs = _paperdiff.get_all_completed_diffs(current_term.id, project_id_list)
    gfk_paper_list = _paper.get_gfk_papers_by_term_project(current_term, project_id_list)
    dealer_dict = {}
    for d in dealer_list:
        dealer_dict[d.id] = d
        d.diff = None
        d.p1 = None
        d.p2 = None
    
    #先从paperdiff找，是否有终审过的问卷对，有则优先采用终审的问卷�
    for di in diffs:
        bmw_paper = di.final_paper
        d = dealer_dict.get(bmw_paper.dealer_id)
        d.diff = di
    paper_list = [] #问卷差异的优先采�
    if len(diffs) > 0:
        paper_list.extend([diff.fw_paper for diff in diffs]) 
        paper_list.extend([diff.fh_paper for diff in diffs]) 
    
    for paper in gfk_paper_list:
        d = dealer_dict.get(paper.dealer_id)
        if d is None or d.diff is not None:
            continue
        if paper.paper_type == mcenums.FW_PAPER_TYPE:
            if d.p1:
                if paper.status > d.p1.status:
                    d.p1 = paper
            else: 
                d.p1 = paper
        elif paper.paper_type == mcenums.FH_PAPER_TYPE:
            if d.p2:
                if paper.status > d.p2.status:
                    d.p2 = paper
            else: 
                d.p2 = paper
    
    paper_list.extend([d.p1 for d in dealer_dict.values() if d.p1])
    paper_list.extend([d.p2 for d in dealer_dict.values() if d.p2])
            
    paper_audits = _paperaudit.getAuditsByPaperList(paper_list)
    for audit in paper_audits:
        d = dealer_dict.get(audit.paper.dealer.id)
        user = audit.user
        for per, name, status in GFK_PERM_AUDITS:
            date_name = '%s_date' % name
            user_name = '%s_id' % name
            if hasattr(d, date_name) == False:
                d.__setattr__(date_name, '')
            if hasattr(d, user_name) == False:
                d.__setattr__(user_name, '')
            if _user.check_user_perm(user, per) and audit.new_status == status:
                d.__setattr__(date_name, audit.created.strftime('%Y-%m-%d'))
                d.__setattr__(user_name, '%s-%s' % (user.username, user.first_name))
                
        if d.diff and d.diff.bmw:
            d.bmw_date = d.diff.updated.strftime('%Y-%m-%d')
            d.bmw_name = '%s-%s' % (d.diff.bmw.username, d.diff.bmw.first_name)
            
    set_dealer_info(dealer_list, competition)
def set_dealer_info(dealer_list, competition):
    for dealer in dealer_list:
        if dealer.diff:
            #无差异和已经解决差异的得�
            dealer.paper_status = dealer.diff.final_paper.get_status_display()
            dealer.p_status = dealer.diff.final_paper.status
            dealer.visite_date = dealer.diff.final_paper.visit_begin
            dealer.report_ready = dealer.diff.final_paper.report_ready
            dealer.visitor_num = dealer.diff.final_paper.visitor_num
            dealer.score = '%.1f' % dealer.diff.final_paper.score
            dealer.paperid = dealer.diff.final_paper.id
        elif dealer.p1:
            dealer.paper_status = dealer.p1.get_status_display()
            dealer.p_status = dealer.p1.status
            dealer.visite_date = dealer.p1.visit_begin
            dealer.report_ready = False
            dealer.visitor_num = dealer.p1.visitor_num
            #竞品无复�
            if dealer.p1.status == mcenums.PAPER_STATUS_FINISH:
                if competition:
                    dealer.score = '%.1f' % dealer.p1.score
                    dealer.report_ready = dealer.p1.report_ready
                else:
                    #只显示无差异，且为终审后的得�
                    if  dealer.p2 is not None  and dealer.p2.score is not None and dealer.p2.score == dealer.p1.score:
                        if dealer.p2.status == mcenums.PAPER_STATUS_FINISH:
                            dealer.score = '%.1f' % dealer.p1.score
                            dealer.report_ready = dealer.p1.report_ready
            dealer.paperid = dealer.p1.id
        else:
            dealer.paper_status = u'尚未访问'
            dealer.report_ready = False
            dealer.p_status = 0

@login_required
def route(request):
    current_term = _term.get_cur_input_term()
    terms_list = _route.getTerms()
    term_id = int(request.POST.get('term', "0"))
    if term_id == 0:
       term_id = terms_list[0].id
    routes_info = _route.getRoutesInfo(term_id)
    users_list = []
    cannot_edit = current_term.id != term_id
#    ok = True  #不能放在这里

    if routes_info and len(routes_info) > 0:
        users_list = _user.getUsers()
    user_infos = []
    user_ids = []  
    for u in users_list:
        user_ids.append(u.id)
        user_infos.append('%s-%s' % (u.username, u.first_name))               
    return locals()


def user_exist(routers, user_id):    #遍历Router表中有没有user_id，有return true
    for router in routers:
        if router.user_id == int(user_id):
            return True
            break
    return False
        
@login_required
def ajax_db_route(request):
    current_term = _term.get_cur_input_term()
    term_id = int(request.POST.get('term', '0'))
    if current_term.id != term_id:
        result = simplejson.dumps({'result':'fail'})
        return HttpResponse(result)
    routes_info = _route.getRoutesInfo(term_id)
    
    for r in routes_info:
        user_id = request.POST.get('router%d' % r.id, None)
        if user_id:
            if user_exist(routes_info, user_id) or r.user:   #如果user_id已经在表中存在，那就不更新表，直接continue
                continue
            update_msg = _route.updateRouter(r.id, user_id)
    result = simplejson.dumps({'result':'ok'})
    return HttpResponse(result)

@login_required
def paper_conflict(request):
    terms = _term.get_list_terms(_term.get_cur_term())
    alltypes = _dealer.get_dealer_types()
    dealertypes = []
    for dt in alltypes:
        if dt.name_en == 'BMW' or dt.name_en == 'MINI':
            dealertypes.append(dt)
    return locals()

@login_required
def ajax_paper_conflict(request):
    term_id = int(request.POST.get('Term', 0))
    type = int(request.POST.get('Wave', 0))
    if type == 1:
        project_id = 2
    elif type == 5:
        project_id = 3
    else:
        project_id = 4
    diffs = _paperdiff.get_all_diffs_need_bmw_APQ(term_id, project_id)
    dealers = []
    for di in diffs:
        fw_paper = di.fw_paper
        dealer = fw_paper.dealer
        dealer.visitor_num = fw_paper.visitor_num
        dealer.user_id = '%s-%s' % (fw_paper.user.username, fw_paper.user.first_name)
        dealer.visitor_date = fw_paper.visit_begin.strftime('%Y-%m-%d')
        dealer.fw_score = '%.1f' % fw_paper.score
        dealer.fh_score = '%.1f' % di.fh_paper.score
        dealer.diff_id = di.id
        if di.final_paper and di.status != mcenums.HAS_CONFLICT:
            dealer.bmw_score = '%.1f' % di.final_paper.score
        dealers.append(dealer)
    return locals()

@login_required
def paper_conflict_detail(request, paperdiff_id):
    paperdiff = PaperDiff.objects.get(pk=paperdiff_id)
    qustiondiffs = _paperdiff.get_all_questiondiff_by_diffid(paperdiff_id)
    questions = []
    
    read_only = paperdiff.status == mcenums.FIXED_CONFLICT
    for qdi in qustiondiffs:
        question = qdi.question
        qustion_cp_dict = _checkpoint.get_question_checkpoint_dict(question.project)
        item = questionitem()
        item.name = question.name_abbr
        cp = qustion_cp_dict.get(question.cid)
        item.desc = cp.desc
        item.desc_en = cp.desc_en
        item.alts = question.alt_list
        if len(item.alts) > 2:
            item.a3 = item.alts.filter(cid='A3')
        if len(item.alts) > 3:
            item.alts = item.alts.exclude(cid='A2')
        item.fw_score = qdi.fw_q_score
        item.fw_comments = _question.restore_result(question, qdi.fw_q_comment)
        if item.fw_comments is None:
            item.fw_comments = '-'
        elif item.fw_score is None or '' == item.fw_score:
            item.fw_comments = u'<strong>不适用</strong><br>%s' % item.fw_comments
        elif item.fw_score == 0:
            #转成str否则页面显示&nbsp;
            item.fw_score = '0.0'
            item.fw_comments = u'<strong>否</strong><br>%s' % item.fw_comments
            
        item.fh_score = qdi.fh_q_score
        item.fh_comments = _question.restore_result(question, qdi.fh_q_comment)
        if item.fh_comments is None:
            item.fh_comments = '-'
        elif item.fh_score is None or '' == item.fh_score:
            item.fh_comments = u'<strong>不适用</strong><br>%s' % item.fh_comments
        elif item.fh_score == 0:
            #转成str否则页面显示&nbsp;
            item.fh_score = '0.0'
            item.fh_comments = u'<strong>否</strong><br>%s' % item.fh_comments
            
        item.bmw_score = qdi.final_q_score
        item.bmw_comments = _question.restore_result(question, qdi.final_q_comment)
        item.fixed = qdi.marked
        if item.bmw_score == 0:
            #转成str否则页面显示&nbsp;
            item.bmw_score = '0.0'
            item.bmw_comments = u'<strong>否</strong><br>%s' % item.bmw_comments
        elif (item.bmw_score is None or '' == item.bmw_score) and item.bmw_comments:
            item.bmw_comments = u'<strong>不适用</strong><br>%s' % item.bmw_comments
        item.qdid = qdi.id
        questions.append(item)
        
    return locals()

class questionitem(object):
    pass

@login_required
def ajax_bmw_update_question(request):
    qdid = int(request.POST.get('qdid', '0'))
    alt_cid = request.POST.get('acid', '0')
    comments = request.POST.get('comments', None)
    
    sdicts = {}
    sdicts['result'] = 0
    
    questiondiffs = QuestionDiff.objects.filter(id=qdid)
    if questiondiffs:
        question = questiondiffs[0].question
    alts = Alternative.objects.filter(cid=alt_cid, question=question)
    if len(alts) > 0 and len(questiondiffs) > 0:
        #1. 更新question diff, score/comments
        qdiff = questiondiffs[0]
        paperdiff = qdiff.paper_diff
        question = qdiff.question
        qustion_cp_dict = _checkpoint.get_question_checkpoint_dict(question.project)
        cp = qustion_cp_dict.get(question.cid)
        part_dict = {}
        if 'A' not in alts[0].cid:
            alt = Alternative.objects.filter(cid='A2', question=question)[0]
            back_comments = u'<strong>否</strong><br>%s<br>%s' % (alts[0].title, comments)
            comments = '%s^-^%s' % (alts[0].cid, comments)
        else:
            alt = alts[0]
            back_comments = u'<strong>不适用</strong><br>%s' % comments
        part_dict[cp.resp_col] = alt.id #设置选中的项id
        qdiff.final_q_score = alt.score
        qdiff.final_q_comment = comments
        if comments:
            part_dict['%s__open' % cp.name] = '"%s"' % comments #设置原因字段
        else:
            part_dict['%s__open' % cp.name] = 'null'#设置原因字段
        qdiff.marked = True
        qdiff.save()
        #2. 更新survey_respondentdata相应问题字段
        try:
            c, con = DbUtils.cursor()
            sql_str = ','.join(['%s=%%(%s)s' % (key, key) for key in part_dict])
            sql = "update survey_respondentdata set %s where id=%s" % (sql_str, paperdiff.final_paper.respondent.id)    
            sql = sql % part_dict
            c.execute(sql)
            if con:
                con.commit()
            #3. 重算环节分，及total,更新paperdiff.final_paper.score 直接调用 _report.gen_papers_score
            _report.gen_papers_score(question.project, [paperdiff.final_paper], c, con)
        finally:
            if c:
                c.close()
            if con:
                con.close() 
        #4.检�paperdiff下是否还有questiondiff，没有审核，若都审核过了，则paperdiff.status置为修复�
        counts = QuestionDiff.objects.filter(paper_diff=paperdiff, marked=False).count()
        if counts == 0:
            paperdiff.status = mcenums.FIXED_CONFLICT
            paperdiff.bmw = request.user
            paperdiff.save()
    
    sdicts['comments'] = back_comments
    sdicts['result'] = 1    
    result = simplejson.dumps(sdicts, ensure_ascii=False)
    return HttpResponse(result)
