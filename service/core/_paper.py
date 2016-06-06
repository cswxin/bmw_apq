#encoding:utf-8

import constant
from service import paperhtml
from survey.models import Respondent
from mc.models import Paper, Report
from mc import enums
from django.contrib.auth.models import User
from service.core import _term

#获得各个部分显示的html,respondent可能为空
def get_paper_part_html(request, part, respondent, paper=None):
    
    html = ''
    methodname = 'get_part_%s_html' % part
    if hasattr(paperhtml, methodname):
        func = getattr(paperhtml, methodname)
        html = func(request, respondent, paper)
    
    return html

#保存相关的respondent数据,respondent可能为空
#返回respondent对象
def save_paper_part_data(request, part, respondent, paper):
    resp = respondent
    if not resp:
        resp = Respondent()
        resp.project_id = request.POST.get('pid', 1)
        resp.user = request.user
        resp.save()
    
    methodname = 'save_part_%s_data' % part
    if hasattr(paperhtml, methodname):
        func = getattr(paperhtml, methodname)
        func(request, resp, paper)
        resp.save()
    
    return resp

def get_paper(**kargs):
    query = Paper.objects.filter(**kargs).order_by('-status')
    if query.count() > 0:
        return query[0]
    return None

def get_papers(**kargs):
    query = Paper.objects.filter(**kargs)
    return query

def get_gfk_papers_by_term_project(term, project_ids):
    paper_list = []
    paper_list = Paper.objects.filter(term=term, project__id__in=project_ids, paper_type__in=[enums.FW_PAPER_TYPE, enums.FH_PAPER_TYPE])
    return paper_list


def get_bmw_papers_by_term_project(term, project_id):
    paper_list = Paper.objects.filter(term=term, project__id__in=project_id, paper_type=enums.BMW_PAPER_TYPE)
    return paper_list

def get_papers_by_term_project_Dealer(term, project_id, type, dealerList=None):
    paper_list = []
    
    if type == 1 or type == 5:
        paper_list = Paper.objects.filter(term=term, dealer__dealertype__id=type, project__id=project_id, paper_type=enums.BMW_PAPER_TYPE, status=enums.PAPER_STATUS_FINISH).exclude(score=None)
    else:
        paper_list = Paper.objects.filter(term=term, dealer__dealertype__id=type, project__id=project_id, paper_type=enums.FW_PAPER_TYPE, status=enums.PAPER_STATUS_FINISH).exclude(score=None)
        
    if paper_list:
        if dealerList:
            paper_list = paper_list.filter(dealer__in=dealerList)
        for paper in paper_list:
            gen_campare_paper_score(paper)
    return paper_list

def get_empty_reports():
    return Report.objects.get_empty_query_set()

def get_report(**kargs):
    query = Report.objects.filter(**kargs)
    if query.count() > 0:
        return query[0]
    return None

def get_reports_by_term_project_Dealer(term, project_id, type, dealerList=None):
    report_list = Report.objects.filter(term=term, dealer__dealertype__id=type, project__id=project_id).exclude(score=None)
        
    if report_list:
        if dealerList:
            report_list = report_list.filter(dealer__in=dealerList)
        for report in report_list:
            gen_campare_report_score(report)
    return report_list

def gen_campare_report_score(report):
    if report.dealer.dealertype.id <= 2:
        report2 = Report.objects.filter(term__id=(report.term.id - 1), dealer=report.dealer)
    else:
        report2 = Report.objects.filter(term__id=(report.term.id - 1), dealer=report.dealer)
    if report2:
        if report.score is not None and report2[0] and report2[0].score is not None :
            report.diffscore = report.score - report2[0].score

def gen_campare_paper_score(paper):
    if paper.dealer.dealertype.id == 1 or paper.dealer.dealertype.id == 5:
        if paper.term.id == 5:
            paper2 = Paper.objects.filter(term__id=(paper.term.id - 1), dealer=paper.dealer, paper_type=enums.FW_PAPER_TYPE)
        else:
            paper2 = Paper.objects.filter(term__id=(paper.term.id - 1), dealer=paper.dealer, paper_type=enums.BMW_PAPER_TYPE)
    else:
        paper2 = Paper.objects.filter(term__id=(paper.term.id - 1), dealer=paper.dealer, paper_type=enums.FW_PAPER_TYPE)
    if paper2:
        if paper.score is not None and paper2[0] and paper2[0].score is not None :
            paper.diffscore = paper.score - paper2[0].score

def add_cur_paper_to_dealers(dealers, term):
    for dealer in dealers:
        dealer.paper = get_cur_paper_by_dealer(dealer, term)
        
def get_cur_paper_by_dealer(dealer, term):
    papers = Paper.objects.filter(dealer=dealer, term=term, paper_type=enums.BMW_PAPER_TYPE)
    if papers:
        return papers[0]
    return None

def get_papers_info(term, project_id, search_list, stype):
    '''统计问卷的各种信息'''
    items = []
    paper_type = enums.BMW_PAPER_TYPE
    if project_id == 4:
        paper_type = enums.FW_PAPER_TYPE
    for search_item in search_list:
        item = Item()
        item.search_item = search_item
        if isinstance(search_item, User):
            #访问员
            papers = get_papers(user=search_item, paper_type=paper_type, term=term, status=enums.PAPER_STATUS_FINISH, dealer__dealertype=stype, project__id=project_id).exclude(score=None)
            item.name = search_item.first_name
            item.papers = papers
            item.url = '<a href="/DealerReport/details/user/%d/%d/%d/%d">点击查看详情<br>Click here for more</a>' % (term.id, project_id, search_item.id, stype.id)
        elif isinstance(search_item, (int, long)):
            #进店人数
            papers = get_papers(visitor_num=search_item, paper_type=paper_type, term=term, status=enums.PAPER_STATUS_FINISH, dealer__dealertype=stype, project__id=project_id).exclude(score=None)
            item.name = search_item
            item.papers = papers
            item.url = '<a href="/DealerReport/details/num/%d/%d/%d/%d">点击查看详情<br>Click here for more</a>' % (term.id, project_id, search_item, stype.id)
        else:
            #新店老店
            termid = _term.get_all_terms().order_by('-id')[0].id
            if 'new' in search_item:
                item.name = u'新店'
                item.url = '<a href="/DealerReport/details/newold/%d/%d/%s/%d">点击查看详情<br>Click here for more</a>' % (term.id, project_id, search_item, stype.id)
                papers = get_papers(dealer__termid__gte=termid, paper_type=paper_type, term=term, status=enums.PAPER_STATUS_FINISH, dealer__dealertype=stype, project__id=project_id).exclude(score=None)
                item.papers = papers
            else:
                item.name = u'老店'
                item.url = '<a href="/DealerReport/details/newold/%d/%d/%s/%d">点击查看详情<br>Click here for more</a>' % (term.id, project_id, search_item, stype.id)
                papers = get_papers(dealer__termid__lt=termid, paper_type=paper_type, term=term, status=enums.PAPER_STATUS_FINISH, dealer__dealertype=stype, project__id=project_id).exclude(score=None)
                item.papers = papers
        if papers:
            item.dealer_num, item.max_score, item.min_score, item.ave_score = get_papers_score_info(papers)
            if item.dealer_num == None:
                item.url = '-'
            items.append(item)
    return items

def get_papers_by_items(stype, item, project, term, dealer_type):
    paper_type = enums.BMW_PAPER_TYPE
    if project.id == 4:
        paper_type = enums.FW_PAPER_TYPE
    papers = []
    if 'user' == stype:
        papers = get_papers(user__id=item, paper_type=paper_type, term=term, status=enums.PAPER_STATUS_FINISH, dealer__dealertype__id=dealer_type).exclude(score=None)
    if 'num' == stype:
        papers = get_papers(visitor_num=item, paper_type=paper_type, term=term, status=enums.PAPER_STATUS_FINISH, dealer__dealertype__id=dealer_type).exclude(score=None)
    if 'newold' == stype:
        termid = _term.get_all_terms().order_by('-id')[0].id
        if 'new' == item:
            papers = get_papers(dealer__termid=termid, paper_type=paper_type, term=term, status=enums.PAPER_STATUS_FINISH, dealer__dealertype__id=dealer_type).exclude(score=None)
        else:
            papers = get_papers(dealer__termid__lt=termid, paper_type=paper_type, term=term, status=enums.PAPER_STATUS_FINISH, dealer__dealertype__id=dealer_type).exclude(score=None)
    return papers
        
def get_papers_score_info(papers):
    dealers = []
    if papers:
        max_score = papers[0].score
        min_score = papers[0].score
        ave_score = papers[0].score
        total_score = 0.0
        for paper in papers:
            dealers.append(paper.dealer)
            score = paper.score
            total_score += score
            if max_score < score:
                max_score = score
            if min_score > score:
                min_score = score
        length = len(set(dealers))
        max_score = '%.1f' % max_score
        min_score = '%.1f' % min_score
        ave_score = '%.1f' % (total_score / len(papers))
    else:
        max_score = None
        min_score = None
        ave_score = None
        length = None
        
    return length, max_score, min_score, ave_score
    
class Item():
    pass
