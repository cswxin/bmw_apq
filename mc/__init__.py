#encoding:utf-8
from django.db import connection
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from models import *
from survey.models import CheckPoint, Alternative, Question
from mc import utils
import DbUtils

current_term = None
def get_cur_term(refresh=False):
    global current_term
    if refresh or current_term is None :
        query = Term.objects.filter(is_active=True).order_by('-id')
        if query.count() > 0:
            current_term = query[0]
        else:
            current_term = Term.objects.all().order_by('-id')[:1][0]
    return current_term

current_input_term = None
def get_cur_input_term(refresh=False):
    global current_input_term
    if refresh or current_input_term is None:
        query = Term.objects.filter(is_active_input=True).order_by('-id')
        if query.count() > 0:
            current_input_term = query[0]
        else:
            current_input_term = Term.objects.all().order_by('-id')[:1][0]
        
    return current_input_term

def get_dealer_types():
    '''经销商类型查询接口，返回值为所有经销商的queryset'''
    return DealerType.objects.all().order_by('id')

def get_terms(current_term=None):
    '''期数查询接口，返回值为所有期的queryset'''
    if not current_term:
        return Term.objects.all().order_by('id')
    else:
        return Term.objects.filter(id__lte=current_term.id).order_by('id')

def get_dealer_count_by_dealertype(dealertype, refresh=False):
    cache_key = 'dealer_count_by_dealertype_%s' % dealertype.id
    if refresh:
        dealer_count = None        
    else:
        dealer_count = cache.get(cache_key)
    
    if dealer_count is None:
        if dealertype.name_en == 'BMW':
            dealer_count = Dealer.objects.filter(dealertype=dealertype).count()
        else:
            dealer_count = 15 #不管竞品对应的经销商有多少,只取15家
        cache.set(cache_key, dealer_count, 24 * 60 * 60)
    #print dealertype,dealer_count
    return dealer_count

DEALERTYPE_BMW = None
def get_dealertype_BMW():
    global DEALERTYPE_BMW
    if DEALERTYPE_BMW is None:
        DEALERTYPE_BMW = DealerType.objects.get(name_en='BMW')
    return DEALERTYPE_BMW

def get_dealer_count_by_region(region, refresh=False):
    cache_key = 'dealer_count_by_region_%s' % region.id
    if refresh:
        dealer_count = None        
    else:
        dealer_count = cache.get(cache_key)
    
    if dealer_count is None:
        all_dealer_id_list = utils.get_sub_leaf_dealer_id_list(region)
        all_bmw_dealer_id_list = [dealer['id'] for dealer in Dealer.objects.filter(dealertype=get_dealertype_BMW(), has_child=False).values('id')]
        id_set = set(all_dealer_id_list) & set(all_bmw_dealer_id_list)
        dealer_count = len(id_set)
        cache.set(cache_key, dealer_count, 24 * 60 * 60)
    return dealer_count

def get_dealertype_done_survey_count(dealertype, term):
    '''按经销商类型汇总的完成数查询接口'''
    return Paper.objects.filter(term=term, status__gt=enums.PAPER_STATUS_INIT, dealer__dealertype=dealertype).count()

def get_regional_done_survey_count(region, term):
    '''按区域汇总的完成数查询接口'''
    sub_dealer_id_list = utils.get_sub_leaf_dealer_id_list(region)
    all_bmw_dealer_id_list = [dealer['id'] for dealer in Dealer.objects.filter(dealertype=get_dealertype_BMW(), has_child=False).values('id')]
    sub_dealer_id_set = set(sub_dealer_id_list) & set(all_bmw_dealer_id_list)
    
    dealer_id_list = [paper['dealer_id'] for paper in Paper.objects.filter(term=term, status__gt=enums.PAPER_STATUS_INIT, dealer__id__in=sub_dealer_id_set).values('dealer_id')]
    return len(set(dealer_id_list))

def get_leaf_dealer_for_bm(region=None):
    dealertype_bm = DealerType.objects.get(name_en='BMW')
    if not region:
        return Dealer.objects.filter(has_child=False, dealertype=dealertype_bm).order_by('listorder', 'id')
    else:
        sub_dealer_id_list = utils.get_sub_leaf_dealer_id_list(region)
        return Dealer.objects.filter(has_child=False, dealertype=dealertype_bm, id__in=sub_dealer_id_list).order_by('listorder', 'id')

def get_leaf_dealer_id_for_bm(region=None):
    dealertype_bm = DealerType.objects.get(name_en='BMW')
    if not region:
        return [dealer.id for dealer in Dealer.objects.filter(has_child=False, dealertype=dealertype_bm).order_by('listorder', 'id')]
    else:
        sub_dealer_id_list = utils.get_sub_leaf_dealer_id_list(region)
        return [dealer['id'] for dealer in Dealer.objects.filter(has_child=False, dealertype=dealertype_bm, id__in=sub_dealer_id_list).order_by('listorder', 'id').values('id')]

def get_region_by_name(region_name):
    try:
        return Dealer.objects.get(name__iexact=region_name.strip())
    except Dealer.DoesNotExist:
        return None

def get_dealer(**kargs):
    try:
        return Dealer.objects.get(**kargs)
    except Dealer.DoesNotExist:
        return None

def get_paper(**kargs):
    query = Paper.objects.filter(**kargs).order_by('-status')
    if query.count() > 0:
        return query[0]
    
    return None

def get_paper_xls(**kargs):
    try:
        return XslReport.objects.get(**kargs)
    except XslReport.DoesNotExist:
        return None

def get_paper_images(**kargs):
    query = ReportImage.objects.filter(**kargs)
    return [x for x in query]

def get_paper_sounds(**kargs):
    query = ReportSound.objects.filter(**kargs)
    return [x for x in query]

def get_checkpoint_group_list():
    cp_list = []
    for cp in CheckPoint.objects.filter(parent=None).order_by('id'):
        cp_list.append(cp)
    return cp_list

def get_checkpoint_group_list_with_total():
    total = CheckPoint()
    total.name = 'Total'
    total.desc = u'最终得分'
    total.desc_en = 'Total Score'
    cp_group_list = [total]
    cp_group_list.extend(get_checkpoint_group_list())
    for i, cp in enumerate(cp_group_list):
        cp.index = i
    return cp_group_list

#SUB_CHECK_POINT_LIST = None
#TODO 得带上project
def get_sub_checkpoint_list(project):
    SUB_CHECK_POINT_LIST = None
    if not SUB_CHECK_POINT_LIST:
        SUB_CHECK_POINT_LIST = list(CheckPoint.objects.filter(has_child=False).order_by('question__id'))
        for i, cp in enumerate(SUB_CHECK_POINT_LIST):
            cp.index = i
    return SUB_CHECK_POINT_LIST

#MAIN_SCORE_COLUMN_STR = None
def get_main_score_column_str():
    MAIN_SCORE_COLUMN_STR = None
    if not MAIN_SCORE_COLUMN_STR:
        field_list = ['total']
        field_list.extend([cp.name for cp in get_checkpoint_group_list()])
        MAIN_SCORE_COLUMN_STR = ','.join(field_list)
    return MAIN_SCORE_COLUMN_STR

#SUB_SCORE_COLUMN_STR = None
def get_sub_score_column_str():
    SUB_SCORE_COLUMN_STR = None
    if not SUB_SCORE_COLUMN_STR:
        SUB_SCORE_COLUMN_STR = ','.join([cp.name for cp in get_sub_checkpoint_list()])
    return SUB_SCORE_COLUMN_STR

def get_total_cp_list():
    return CheckPoint.objects.order_by('id')

def get_dealer_parent_dict():
    return dict([(dealer.id, dealer.parent_id) for dealer in Dealer.objects.all()])

def get_report_score(report_id):
    sql = 'select %s from mc_reportdata where id=%s;' % (get_main_score_column_str(), report_id)
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

def get_report_sub_score(report_id):
    sql = 'select %s from mc_reportdata where id=%s;' % (get_sub_score_column_str(), report_id)
    try:
        c, con = DbUtils.cursor()
        c.execute(sql)
        ret = c.fetchone()
    finally:
        if c:
            c.close()
        if con:
            con.close() 
    return ret

def get_dealer_score(term, dealer):
    query = Report.objects.filter(term=term, dealer=dealer).order_by('-id')
    if len(query) > 0:
        report = query[0]
        return get_report_score(report.id)
    else:
        return None

def get_dealer_sub_score(term, dealer):
    query = Report.objects.filter(term=term, dealer=dealer).order_by('-id')
    if len(query) == 0:
        return None
    else:
        report = query[0]
        return get_report_sub_score(report.id)

def get_city_score(term, dealer):
    query = Report.objects.filter(term=term, dealer=dealer.city).order_by('-id')
    if len(query) == 0:
        return None
    else:
        report = query[0]
    return get_report_score(report.id)

def get_region_score(term, dealer):
    query = Report.objects.filter(term=term, dealer=dealer.region).order_by('-id')
    #print len(query)
    if len(query) == 0:
        return None
    else:
        report = query[0]
    return get_report_score(report.id)

def get_region_sub_score(term, dealer):
    query = Report.objects.filter(term=term, dealer=dealer.region).order_by('-id')
    if len(query) == 0:
        return None
    else:
        report = query[0]
    return get_report_sub_score(report.id)

def get_national_score(term, dealer):
    query = Report.objects.filter(term=term, dealer=dealer.nation).order_by('-id')
    if len(query) == 0:
        return None
    else:
        report = query[0]
    return get_report_score(report.id)
    
def get_national_sub_score(term, dealer):
    query = Report.objects.filter(term=term, dealer=dealer.nation).order_by('-id')
    if len(query) == 0:
        return None
    else:
        report = query[0]
    return get_report_sub_score(report.id)
    
def get_bmw_top_score(term, checkpoint=None):
    column = checkpoint.name if checkpoint else 'total'
    term_id = term.id
    
    dealertype_id = get_dealertype_BMW().id
    sql = 'select max(data.%(column)s) from mc_report r,mc_reportdata data where r.term_id=%(term_id)s and r.id=data.id and r.dealertype_id=%(dealertype_id)s;' % vars()
    try:
        c, con = DbUtils.cursor()
        c.execute(sql)
        ret = c.fetchone()[0]
    finally:
        if c:
            c.close()
        if con:
            con.close() 
    return ret

def get_zero_reason(term, dealer, checkpoint):
    paper = get_paper(term=term, dealer=dealer)
    try:
        result = paper.respondent.get_data('%s__open' % checkpoint.name)
        result_en = paper.respondent.get_translation(checkpoint.name)
    except:
        result = '-'
        result_en = '-'
    return result or '', result_en or ''

def get_customer_feedback(paper):
    A1_result = paper.respondent.get_data('G50__A1')
    A1_result_en = paper.respondent.get_translation('G50_A1')
    A2_result = paper.respondent.get_data('G50__A2')
    A2_result_en = paper.respondent.get_translation('G50_A2')
    result = []
    dict = {}
    dict['answer'] = A1_result or ''
    dict['answer_en'] = A1_result_en or ''
    result.append(dict)
    dict2 = {}
    dict2['answer'] = A2_result or ''
    dict2['answer_en'] = A2_result_en or ''
    result.append(dict2)
    return result
    
ROOT_DEALER = None
def get_root_dealer():
    global ROOT_DEALER
    if ROOT_DEALER is None:
        ROOT_DEALER = Dealer.objects.filter(parent=None).order_by('listorder', 'id')[:1][0]
    return ROOT_DEALER

def get_regionals():
    '''区域查询接口，返回值为4大区域的queryset'''
    return Dealer.objects.filter(parent=get_root_dealer())

def get_sub_node(parent_node_id, type):
    '''dealer类型的子节点查询接口，返回值为queryset
    @param parent_node_id:父节点dealer类型的ID值
    @param type:查询类型："area"或"dealer"
    '''
    if type == "area":
        return Dealer.objects.filter(parent=parent_node_id)
    elif type == "dealer":
        return Dealer.objects.filter(parent=parent_node_id).filter(has_child=0)
    
def get_detailed_fieldwork_status(dealer_type_tuple, term_id):
    '''提供某一种或多种类型的经销商执行进度的查询接口，返回值为（经销商代码，城市，省份，经销商名称，访问状态，访问日期，报告）类型的queryset
    @param dealer_type_tuple:经销商类型ID值组成的tuple
    @param term_id:期数ID值
    '''
    try:
        c, con = DbUtils.cursor()
        if len(dealer_type_tuple) == 1:
            dealer_type_tuple = dealer_type_tuple[0]
            c.execute('SELECT mc_dealer.name, mc_dealer.city_cn, mc_dealer.city_en, mc_dealer.province_cn, mc_dealer.province_en, mc_dealer.name_cn, mc_dealer.name_en, mc_report.status, survey_respondent.start_time, mc_report.survey_code FROM mc_dealer LEFT JOIN mc_report ON  mc_dealer.id = mc_report.dealer_id LEFT JOIN survey_respondent ON mc_report.respondent_id = survey_respondent.id AND mc_report.term_id= %s WHERE mc_dealer.dealertype_id = %s' % (term_id, dealer_type_tuple))
        else:
            c.execute('SELECT mc_dealer.name, mc_dealer.city_cn, mc_dealer.city_en, mc_dealer.province_cn, mc_dealer.province_en, mc_dealer.name_cn, mc_dealer.name_en, mc_report.status, survey_respondent.start_time, mc_report.survey_code FROM mc_dealer LEFT JOIN mc_report ON  mc_dealer.id = mc_report.dealer_id LEFT JOIN survey_respondent ON mc_report.respondent_id = survey_respondent.id AND mc_report.term_id= %s WHERE mc_dealer.dealertype_id IN %s' % (term_id, dealer_type_tuple))
        result = c.fetchall()
    finally:
        if c:
            c.close()
        if con:
            con.close() 
    return result

def get_regional_report_document(areacode):
    '''提供某个区域内的所有report_document的查询接口，返回值为ReportDocument的queryset
    @param areacode:区域数值，具体详见mc.enums.CHOICES_AREA_TYPE
    '''
    return ReportDocument.objects.filter(areacode=areacode)

def get_dealer_reports(dealer_type_tuple, regional, term_id):
    '''提供某一种或多种类型的经销商访问情况报告的查询接口，返回值为（经销商代码，城市，省份，经销商名称，经销商本期最终得分，报告）类型的queryset
    @param dealer_type_tuple:经销商类型ID值组成的tuple
    @param regional:区域对象
    @param term_id:期数ID值
    '''
    try:
        c, con = DbUtils.cursor()
        dealer_id_list = utils.get_sub_leaf_dealer_id_list(regional)
        dealer_id_list = tuple(dealer_id_list)
        if len(dealer_type_tuple) == 1:
            dealer_type_tuple = dealer_type_tuple[0]
            c.execute('SELECT mc_dealer.name, mc_dealer.city_cn, mc_dealer.city_en, mc_dealer.province_cn, mc_dealer.province_en, mc_dealer.name_cn, mc_dealer.name_en, mc_reportdata.total, mc_report.survey_code FROM mc_dealer LEFT JOIN mc_report ON mc_dealer.id = mc_report.dealer_id LEFT JOIN mc_reportdata ON mc_report.id = mc_reportdata.id AND mc_report.term_id= %s WHERE mc_dealer.id in %s AND mc_dealer.dealertype_id = %s' % (term_id, dealer_id_list, dealer_type_tuple))
        else:
            c.execute('SELECT mc_dealer.name, mc_dealer.city_cn, mc_dealer.city_en, mc_dealer.province_cn, mc_dealer.province_en, mc_dealer.name_cn, mc_dealer.name_en, mc_reportdata.total, mc_report.survey_code FROM mc_dealer LEFT JOIN mc_report ON mc_dealer.id = mc_report.dealer_id LEFT JOIN mc_reportdata ON mc_report.id = mc_reportdata.id AND mc_report.term_id= %s WHERE mc_dealer.id in %s AND mc_dealer.dealertype_id in %s' % (term_id, dealer_id_list, dealer_type_tuple))
        result = c.fetchall()
    finally:
        if c:
            c.close()
        if con:
            con.close() 
    return result

def get_dealer_info_for_comare(dealer_id, term):
    try:
        dealer = Dealer.objects.get(id=dealer_id)
        paper = Paper.objects.get(dealer=dealer, term=term)
    except ObjectDoesNotExist:
        return False
    result = {'city_cn':dealer.city_cn,
              'city_en':dealer.city_en,
              'province_cn':dealer.province_cn,
              'province_en':dealer.province_en,
              'name_cn':dealer.name_cn,
              'name_en':dealer.name_en,
              'status':paper.status}
    return result

#获得一个问卷
def get_paper_by_id(paperid):
    paper = None
    try:
        paper = Paper.objects.get(id=paperid)
    except Paper.DoesNotExist:
        pass
    
    return paper

#提交一个问卷
def submit_paper(paper, user):
    if user.id == paper.user.id:
        from service.core._user import has_fw_input_perm, has_fh_input_perm
        if has_fw_input_perm(user):
            paper.status = enums.FW_PAPER_STATUS_WAIT_AUDIT_1
            paper.paper_type = enums.FW_PAPER_TYPE
        elif has_fh_input_perm(user):
            paper.status = enums.FH_PAPER_STATUS_WAIT_AUDIT_1
            paper.paper_type = enums.FH_PAPER_TYPE
        else:
            return False
        #保存审核记录
        save_paper_audit_status(paper, user, paper.status)
        #修改paper的状态
        paper.save()
        return True
    
    return False

#生成单店报告 
def gen_report(paper, user):
    from mc.excel.gen_dealer_report import gen_dealer_report_file
    dealer = paper.dealer
    term = paper.term
    filepath = gen_dealer_report_file(paper)
    
    xls, create = XslReport.objects.get_or_create(paper=paper)
    xls.xslfile = filepath
    xls.save()
    return filepath

def gen_csv(paper, csv_file_name):
    import csv
    file = csv.writer(file(csv_file_name), 'wb', delimiter=',',)
    terms = ['', '第1期\r\n1st Wave', '第2期\r\n2nd Wave', '第3期\r\n3rd Wave', '第4期\r\n4th Wave', '第5期\r\n5th Wave']
    file.writerows(['by basic', '最终得分'])
    file.writerow(terms)
    
    
#获得期数
def get_term_by_respondent(respondent):
    if respondent:
        try:
            paper = Paper.objects.get(respondent=respondent)
            return paper.term
        except Paper.DoesNotExist:
            pass
    
    return get_cur_input_term()

#保存审核记录
def save_paper_audit_status(paper, user, status):    
    pa, create = PaperAudit.objects.get_or_create(paper=paper, new_status=status)
    pa.old_status = paper.status
    pa.user = user
    pa.save()    

#获得审核历史记录
def get_audit_history(respondent):
    if not respondent:
        return []
    
    try:
        paper = Paper.objects.get(respondent=respondent)
    except Paper.DoesNotExist:
        return []
    
    pas = [a for a in PaperAudit.objects.filter(paper=paper)]
    audits = []
    is_fh_paper = paper.paper_type == enums.FH_PAPER_TYPE
    for status, name in enums.AUDIT_PAPER_STATUS:
        if is_fh_paper:
            if  status < enums.FH_PAPER_STATUS_INPUT:
                continue
        else:
            if status >= enums.FH_PAPER_STATUS_INPUT and status != enums.PAPER_STATUS_FINISH:
                continue
        pa = _get_audit_item(pas, status)
        if pa is None:
            pa = PaperAudit()
        
        pa.name = name
        audits.append(pa)
    return audits

def _get_audit_item(pas, status):
    for pa in pas:
        if pa.new_status == status:
            return pa
    
    return None

def get_history_report(dealer_id):
    reports = XlsReportHist.objects.filter(dealer=dealer_id).order_by('term_index')
    return reports

def download_history_report(list):
    reports = XlsReportHist.objects.filter(pk__in=list)
    return reports

def get_all_history_reports():
    return XlsReportHist.objects.all()


cp_group_term_score_dict = {}
def get_cp_group_term_score(dealer, term, checkpoint):
    key = (dealer.id, term.id)
    score_list = cp_group_term_score_dict.get(key)
    if score_list is None:
        score_list = get_dealer_score(term, dealer)
        cp_group_term_score_dict[key] = score_list
    
    if score_list is None:
        return 0
    
    return score_list[checkpoint.index]

def get_sub_cp_index_dict():
    SUB_CP_INDEX_DICT = {}
    if not SUB_CP_INDEX_DICT:
        sub_cp_list = get_sub_checkpoint_list()
        for i, cp in enumerate(sub_cp_list):
            SUB_CP_INDEX_DICT[cp.id] = i
    return SUB_CP_INDEX_DICT

def get_cp_child_term_score(dealer, term, checkpoint):
    score_list = get_dealer_sub_score(term, dealer)
    if score_list is None:
        return 0
    
    sub_cp_index_dict = get_sub_cp_index_dict()
    return score_list[sub_cp_index_dict.get(checkpoint.id)]

def get_dealer_data(curr_dealer, curr_term=None):
    dealer = curr_dealer
    cp_list = get_checkpoint_group_list_with_total()
    question_list = get_sub_checkpoint_list()
    term_list = list(get_terms(curr_term))
    if curr_term == None:
        curr_term = term_list[-1]
    
    paper = get_paper(term=curr_term, dealer=dealer)
    if not paper:
        #尚未录入问卷
        return {}
    

    
    for cp in cp_list:
        cp.score_list = []
        cp.score_list_nation = []
        cp.score_list_city = []
        cp.score_list_region = []
        cp.score_list_top = []
        for i in range(4):
            if i < len(term_list):
                score = get_cp_group_term_score(dealer, term_list[i], cp)
                score_nation = get_cp_group_term_score(dealer.nation, term_list[i], cp)
                score_region = get_cp_group_term_score(dealer.region, term_list[i], cp)
                score_city = get_cp_group_term_score(dealer.city, term_list[i], cp)
                score_top = get_bmw_top_score(term_list[i], cp)
            else:
                score = ''
                score_nation = ''
                score_region = ''
                score_city = ''
                score_top = ''
            if i + 1 == curr_term.id:
                curr_term.score = score_nation
            cp.score_list.append('%.1f' % score if score else '')
            cp.score_list_nation.append('%.1f' % score_nation if score_nation else '')
            cp.score_list_region.append('%.1f' % score_region if score_region else '')
            cp.score_list_city.append('%.1f' % score_city if score_city else '')
            cp.score_list_top.append('%.1f' % score_top if score_top else '')
        
        cp.sub_cp_list = []
        for sub_cp in cp.child_list:
            sub_cp.score_list = []
            for i in range(4):
                if i < len(term_list):
                    score = get_cp_child_term_score(dealer, term_list[i], sub_cp)
                    sub_cp.score_list.append('%.1f' % score if score is not None else u'不适用')
                else:
                    score = '-'
                    sub_cp.score_list.append(score)
            
            score = get_cp_child_term_score(dealer, curr_term, sub_cp)
            sub_cp.zero_reason = ''
            sub_cp.zero_reason_en = ''
            if not score:
                sub_cp.zero_reason, sub_cp.zero_reason_en = get_zero_reason(curr_term, dealer, sub_cp)
            cp.sub_cp_list.append(sub_cp)
    
    curr_term.score = cp_list[0].score_list[curr_term.id - 1]
    
    
    for cp in question_list:
        score = get_cp_child_term_score(dealer, curr_term, cp)
        cp.score = '%.1f' % score if score is not None else u'不适用'
        #~ print cp.name,score
        
        score_nation = get_cp_child_term_score(dealer.nation, curr_term, cp)
        cp.score_nation = '%.1f' % score_nation if score_nation is not None else '-'
        
        score_region = get_cp_child_term_score(dealer.region, curr_term, cp)
        cp.score_region = '%.1f' % score_region if score_region is not None else '-'
        
        if cp.score != '100.0':
            cp.zero_reason, cp.zero_reason_en = get_zero_reason(curr_term, dealer, cp)
        else:
            cp.zero_reason, cp.zero_reason_en = '', ''
        
        if score is not None:
            if score_nation:
                nation_delta = score - score_nation
            else:
                nation_delta = 0
            cp.nation_delta = '%.1f' % nation_delta
            
            if score_region:
                region_delta = score - score_region
            else:
                region_delta = 0
            
            cp.region_delta = '%.1f' % region_delta
    
    
    #新增题
    q1 = Question.objects.get(cid='A52')
    q2 = Question.objects.get(cid='B53')
    q3 = Question.objects.get(cid='C54')
    q4 = Question.objects.get(cid='E55')
    qs = [q1, q2, q3, q4]
    ck_new = []
    for q in qs:
        ck1 = CheckPoint(question=q)
        ck1.name = q.cid
        ck1.desc = q.title
        ck1.score = '100.0'
        ck1.score_region = '0.0'
        ck1.score_nation = '0.0'
        ck1.zero_reason = ''
        ck_new.append(ck1)
        
        pos = get_pos(question_list, q.cid)
        question_list.insert(pos, ck1)
    
    respond = paper.respondent
    
    #新增题答案翻译
    tran_q_a52 = respond.get_translation('A52')
    tran_q_e55 = respond.get_translation('E55')
    tran_q_b53 = respond.get_translation('B53')
    tran_q_c54 = respond.get_translation('C54')
    #新增题答案
    q_a52 = respond.get_data('A52')
    q_e55 = respond.get_data('E55')
    q_b53 = respond.get_data('B53')
    q_c54 = respond.get_data('C54')
    
    try:
        q_a52 = Alternative.objects.get(id=q_a52).title
    except:
        q_a52 = ""
    try:
        q_e55 = Alternative.objects.get(id=q_e55).title
    except:
        q_e55 = ""
    try:
        q_b53 = Alternative.objects.get(id=q_b53).title
    except:
        q_b53 = ""
    try:
        q_c54 = Alternative.objects.get(id=q_c54).title
    except:
        q_c54 = ""        
    
    if q_a52 == u'是':
        q_a52_comment = ''
    else:
        q_a52_comment = respond.get_data('A52__open')
    
    if q_e55 == u'是':
        q_e55_comment = ''
    else:
        q_e55_comment = respond.get_data('E55__open')
    
    if q_b53 == u'是':
        q_b53_comment = ''
    else:
        q_b53_comment = respond.get_data('B53__open')
    
    if q_c54 == u'是':
        q_c54_comment = ''
    else:
        q_c54_comment = respond.get_data('C54__open')    
    
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
    
    #获得第三期的新增数据
    ps = Paper.objects.filter(dealer=curr_dealer, term__id=3)
    if ps.count() > 0:
        p = ps[0]
        r = p.respondent
        #新增题答案
        q_a52_3 = r.get_data('A52')
        q_e55_3 = r.get_data('E55')
        q_b53_3 = r.get_data('B53')
        q_c54_3 = r.get_data('C54')
        
        try:
            q_a52_3 = Alternative.objects.get(id=q_a52_3).title
        except:
            q_a52_3 = ""
        try:
            q_e55_3 = Alternative.objects.get(id=q_e55_3).title
        except:
            q_e55_3 = ""
        try:
            q_b53_3 = Alternative.objects.get(id=q_b53_3).title
        except:
            q_b53_3 = ""
        try:
            q_c54_3 = Alternative.objects.get(id=q_c54_3).title
        except:
            q_c54_3 = ""
    
    return locals()




#或获得当前期数以前的列表
def get_list_terms(current_term):
    query = Term.objects.filter(id__lte=current_term.id)
    return query

#获得第3期的h部分试题
def get_h3_question():
#    from tools.add_q3_question import question_list
#    from survey.models import Question
#    cids = []
#    for cid,name in question_list[4:]:
#        cids.append(cid)
#    
#    qs = Question.objects.filter(cid__in=cids).distinct()
#    return qs
    pass

def is_q3(paper):
    termid = 3
    if paper:
        termid = paper.term_id
        if not termid:
            termid = 3
    
    if termid >= 3:
        return True
    else:
        return False

def is_2012(paper):
    projectid = 2
    if paper:
        projectid = paper.project_id
        if not projectid:
            projectid = 2
    
    if projectid > 1:
        return True
    else:
        return False

def get_paper_project_id(paper):
    projectid = 2
    if paper:
        projectid = paper.project_id
        if not projectid:
            projectid = 2
    return projectid
    
def get_dealer_score_info(dealer, curr_term, cp, paper):
    try:
        c, con = DbUtils.cursor()
        sql = 'select %s from survey_respondentdata where id=%d;' % (cp.name, paper.respondent_id)
        c.execute(sql)
        ret = c.fetchone()
    finally:
        if c:
            c.close()
        if con:
            con.close() 
    aid = ret[0]
    
    a = Alternative.objects.get(id=aid)
    #print 'a.title',a.title
    cp.dealer_score = a.title
    if cp.dealer_score == u'是':
        cp.zero_reason = ''
        cp.zero_reason_en = ''
    else:
        cp.zero_reason, cp.zero_reason_en = get_zero_reason(curr_term, dealer, cp)
    
#获得位置
def get_pos(sub_cp_list, cid):
    c = cid[0]
    pos = 0
    begin = 0
    i = 0
    for cp in sub_cp_list:
        qcid = cp.name
        
        if qcid.startswith(c):
            begin += 1
        else:
            if begin:
                pos = i
                break
        
        i += 1
    
    return pos
