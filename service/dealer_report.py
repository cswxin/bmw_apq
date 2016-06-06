#encoding:utf-8
from django.shortcuts import HttpResponseRedirect, Http404, HttpResponse, render_to_response
from django.http import HttpResponseNotFound
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.template import RequestContext
from django.utils import simplejson
from mcview.decorator import render_to
import copy, os
from mcview.chart_utils import create_multi_xychart, create_simple_xychart, create_history_now_future_xychart
from service.core import _term, _user, _paper, _dealer, _checkpoint, _question, _report, _project
from mc import enums
from mc.models import Dealer, PaperDiff, Report, OtherReport, XslReport
from survey.models import CheckPoint, Project
import mc
import settings
import constant
from userpro.models import UserProfile
from lxml.html.formfill import _check
from django.forms.models import model_to_dict
from service import easyExcel
from service.easyExcel import easyExcel
import cStringIO
import cPickle as pickle
import datetime
from service.chart_utils import create_bar_line_xychart
from mc.models import Term

def pyobj_to_str(pyobj):
    '''将对象序列化'''
    buffers = cStringIO.StringIO()
    pickle.dump(pyobj, buffers)
    return buffers.getvalue()

def str_to_pyobj(astr):
    '''将字符串转成对象'''
    if isinstance(astr, unicode):
        buffers = cStringIO.StringIO(astr.encode('utf-8'))
    else:
        buffers = cStringIO.StringIO(astr)
    pyobj = pickle.load(buffers)
    buffers.close()
    return pyobj

@login_required
def index(request):
    user = request.user
    dealerPagePerm = _user.has_dealer_page_perm(user)
    return locals()
@login_required
def dealer_analysis(request):
    user = request.user
    dealer = _dealer.get_dealer_by_username(user.username)
    term = _term.get_cur_term()
    if dealer:
        paper = _paper.get_paper(dealer=dealer, term=term, paper_type=enums.BMW_PAPER_TYPE)
        if paper:
            return report(request, paper.id)
    return locals()

@login_required
def advanced_filter(request):
    regional_name = constant.data_compare_regional_name
    province_name = constant.data_compare_province_name
    city_name = constant.data_compare_city_name
    subdistrict_name = constant.data_compare_subdistrict_name
    dealergroup_name = constant.data_compare_dealergroup_name
    brand_name = constant.data_compare_brand_name
    user_name = constant.data_compare_user_name
    num_name = constant.data_compare_num_name
    newold_name = constant.data_compare_newold_name

    return locals()

@login_required
def advanced_analysis(request):
    return locals()

@login_required
def dealer_filter(request):
    terms = _term.get_list_terms(_term.get_cur_term())
    dealertypes = _dealer.get_dealer_types()

    user = request.user
    up, create = UserProfile.objects.get_or_create(user=user)
    man_dealer = up.dealer
    man_dealer_list = Dealer.objects.filter(name=man_dealer.name)
    #全国
    if man_dealer and man_dealer.level == 0:
        regions = Dealer.objects.filter(level=1)
        provinces = Dealer.objects.filter(level=5)
        citys = Dealer.objects.filter(level=2)
        groups = Dealer.objects.filter(level=6)
        areas = Dealer.objects.filter(level=4)
    #大区    
    if man_dealer and man_dealer.level == 1:
        regions = [man_dealer]
        provinces = Dealer.objects.filter(sf_parent=man_dealer, level=5)
        citys = Dealer.objects.filter(sf_parent__sf_parent=man_dealer, level=2)

        dealers = Dealer.objects.filter(parent__parent=man_dealer, level=3)
        jt_id_list = [d.jt_parent.id for d in dealers if d.jt_parent]
        groups = Dealer.objects.filter(id__in=jt_id_list, level=6)

        areas = Dealer.objects.filter(xq_parent=man_dealer, level=4)
    #小区   
    if man_dealer and man_dealer.level == 4:
        regions = [man_dealer.xq_parent]
        provinces = Dealer.objects.filter(sf_parent=man_dealer.xq_parent, level=5)
        citys = Dealer.objects.filter(sf_parent__sf_parent=man_dealer.xq_parent, level=2)

        dealers = Dealer.objects.filter(xq_parent=man_dealer, level=3)
        jt_id_list = [d.jt_parent.id for d in dealers if d.jt_parent]
        groups = Dealer.objects.filter(id__in=jt_id_list, level=6)

        areas = [man_dealer]
    #经销商  
    if man_dealer and man_dealer.level == 3:
        regions = [man_dealer.parent.parent]
        provinces = [man_dealer.sf_parent.sf_parent]
        citys = [man_dealer.parent]
        groups = [man_dealer.jt_parent for man_dealer in man_dealer_list if man_dealer.jt_parent]
        areas = [man_dealer.xq_parent]

    return locals()

def get_data(request, dtype):
    dataid = 0
    data = request.POST.get(dtype, 0)
    if data:
        dataid = int(data)
    return dataid

@login_required
def ajax_filter(request):
    term_id = int(request.POST.get('Term', 0))
    type_id = int(request.POST.get('Type', 0))

    region_id = get_data(request, 'Region')
    province_id = get_data(request, 'Province')
    city_id = get_data(request, 'City')
    group_id = get_data(request, 'Group')
    area_id = get_data(request, 'Area')

    project_id = constant.dealertype_id_to_project_id(type_id)
    if term_id == 5 and type_id == 1:
        project_id = 3
    if term_id == 5 and type_id == 2:
        project_id = 4
    user = request.user
    up, create = UserProfile.objects.get_or_create(user=user)
    man_dealer = up.dealer

    report_list = Report.objects.filter(term__id=term_id, project__id=project_id, dealertype__id=type_id, dealer__has_child=False)
    if man_dealer.level == 1:
        report_list = report_list.filter(dealer__parent__parent=man_dealer)
    if man_dealer.level == 4:
        report_list = report_list.filter(dealer__xq_parent=man_dealer)
    if man_dealer.level == 3:
        report_list = report_list.filter(dealer__name=man_dealer.name)

    if region_id:
        report_list = report_list.filter(dealer__parent__parent__id=region_id)
    if province_id:
        report_list = report_list.filter(dealer__sf_parent__sf_parent__id=province_id)
    if city_id:
        report_list = report_list.filter(dealer__parent__id=city_id)
    if group_id:
        report_list = report_list.filter(dealer__jt_parent__id=group_id)
    if area_id:
        report_list = report_list.filter(dealer__xq_parent__id=area_id)

    for report in report_list:
        d = report.dealer
        report.top3 = gen_top3_by_term(term_id, project_id, d)
        if d.new_old:
            if d.new_old == u'新店':
                d.newold = u'新店<br> New dealer'
            elif d.new_old == u'老店':
                d.newold = u'老店<br> Old dealer'
    return locals()

def gen_top3_by_term(term_id, project_id, dealer):
    term_list = map(copy.copy, _term.get_2012_farward_term_list(term_id))
    project = Project.objects.get(id=int(project_id))
    for term in term_list:
        report_list = Report.objects.filter(term=term, project=project, dealer=dealer)
        if report_list:
            term.dealer_score = report_list[0].score
        else:
            term.dealer_score = -1
        term.dscore = term.dealer_score

    top3 = gen_top3(term_list)
    return top3

def policy_control (request, check_term):
    term = _term.get_cur_term()
    if term.id != check_term.id:
        return False
    flag = False
    import datetime
    now = datetime.datetime.now()
    timelimits = term.end and term.end > now
    if timelimits:#时间未到
        if term.testonly:#经销商限制
            #语法ip在授权ip内
            remoteip = request.META['REMOTE_ADDR']
            from policy.models import AuthorizedIp
            nums = AuthorizedIp.objects.filter(ip=remoteip, enable=True).count()
            flag = nums <= 0
    return flag
@login_required
def dealer_list(request):
    term = _term.get_cur_term()
    #经销商在时间未到之前只能看到上一期数据
    limited = policy_control(request, term)
    if limited:
        term = _term.get_term_by_id(term.id - 1)

    user = request.user
    dealerPagePerm = _user.has_dealer_page_perm(user)

    dealerList = []
    chargedDealer = _user.get_dealer_by_user(user)
    if chargedDealer:
        if chargedDealer.has_child:
            subs = _dealer.get_sub_leaf_dealer_list(chargedDealer)
            dealerList.extend(subs)
        else:
            dealerList.append(chargedDealer)
            subs = Dealer.objects.filter(name=chargedDealer.name)
            dealerList.extend(subs)
    temp = []
    dealertypedict = {}
    for index, d in enumerate(dealerList):
        dtlist = dealertypedict.get(d.dealertype)
        if dtlist is None:
            dtlist = []
            dealertypedict[d.dealertype] = dtlist
        dtlist.append(d)
        temp.append(d.id)

    dealerList = term.dealers.filter(id__in=temp)

    reports = _paper.get_empty_reports()
    for dt in dealertypedict.keys():
        type_id = dt.id
        project_id = constant.dealertype_id_to_project_id(type_id)
        dtreports = _paper.get_reports_by_term_project_Dealer(term.id, project_id, type_id, dealerList)
        reports = reports | dtreports
    for d in dealerList:
        rps = reports.filter(dealer=d)
        if rps:
            d.report = rps[0]
    return locals()

def gen_top3(term_list):
    top3 = '-'
    score_list = [ ]
    for t in term_list:
        if t.dscore == -1:
            continue
        score_list.append(t.dscore)
    total = 0.0
    count = len(score_list)
    for score in score_list:
        if score == -1:
            count -= 1
            continue
        total += score
    if count <= 0:
        top3 = '-'
    else:
        top3 = total / count
    return top3

__s_date = datetime.date(1899, 12, 31).toordinal() - 1

def getdate(date, format="%Y-%m-%d"):
    if isinstance(date, (int, float)):
        date = int(date)
        d = datetime.date.fromordinal(__s_date + date)
        return d.strftime(format)
    else:
        return date

def getdatetime(date, format="%Y-%m-%d %H:%M:%S"):
    #from matplotlib.dates import num2date
    delta = datetime.timedelta(days=(date - 2))
    d1900 = datetime.datetime(1900, 1, 1, 0, 0, 0)
    str = (d1900 + delta).strftime(format)
    if type(date) == float:
        return (d1900 + delta).strftime(format)
    else:
        return ''

def gettime(date, format="%H:%M"):
    #from matplotlib.dates import num2date
    if type(date) == float:
        delta = datetime.timedelta(days=(date))
        d1900 = datetime.datetime(1900, 1, 1, 0, 0, 0)
        str = (d1900 + delta).strftime(format)
        return (d1900 + delta).strftime(format)
    else:
        return date

@login_required
def report(request, report_id):
    dealerPagePerm = _user.has_dealer_page_perm(request.user)
    report = _paper.get_report(id=int(report_id))
    if report is None:
        return locals()
    images = []
    sounds = []
    dealer = report.dealer
    current_term = report.term
    if current_term.id < 5:
        year = 2014
    else:
        year = 2015
    term = current_term
    if dealerPagePerm :
        limited = policy_control(request, current_term)
        if limited:
            from django.core.exceptions import PermissionDenied
            errorstring = u'亲，未卜先知的你，一个不小心，就误入火星地界。真是没办法呀。请火速返回地球吧。<br>PS：%s开放时间为 %s。届时欢迎访问。谢谢。' % (current_term.name, current_term.end.strftime('%Y-%m-%d %H:%M'))
            return HttpResponse(errorstring)

    has_full_perm = _user.has_all_page_perm(request.user) or _user.has_run_page_perm(request.user)

    dealer_score_dict = {}
    dealer_score_str = report.score_str
    if dealer_score_str:
        dealer_score_dict = str_to_pyobj(dealer_score_str)

    report_region_list = Report.objects.filter(dealertype=dealer.dealertype, term=term, dealer=dealer.parent.parent)
    region_score_dict = {}
    if report_region_list:
        report_region = report_region_list[0]
        report_score_str = report_region.score_str
        if report_score_str:
            region_score_dict = str_to_pyobj(report_score_str)

    report_nation_list = Report.objects.filter(dealertype=dealer.dealertype, term=term, dealer__level=0)
    nation_score_dict = {}
    if report_nation_list:
        report_nation = report_nation_list[0]
        nation_score_str = report_nation.score_str
        if nation_score_str:
            nation_score_dict = str_to_pyobj(nation_score_str)
    if current_term.id == 5:
        query = Term.objects.filter(id=current_term.id)
    else:
        query = Term.objects.filter(id__lte=current_term.id)
    term_list = map(copy.copy, query)
    for term in term_list:
        report_list = Report.objects.filter(term=term, dealer=dealer)
        if report_list:
            term.dealer_score = report_list[0].score
            term.dscore = term.dealer_score
        else:
            term.dealer_score = 0
            term.dscore = -1
        term.region_score = region_score_dict.get('score', 0)
        term.nation_score = nation_score_dict.get('score', 0)

    top3 = gen_top3(term_list)

    term_compare_chart_img = make_term_compare_chart(term_list, dealer)

    cp_group_list = make_dealer_charts(term_list, report)

    sub_cp_list = map(copy.copy, _checkpoint.get_sub_checkpoint_list(report.project.id))

    dealer_answer_dict = {}
    dealer_answer_str = report.answer_str
    if dealer_answer_str:
        dealer_answer_dict = str_to_pyobj(dealer_answer_str)
        time_in = dealer_answer_dict.get('time_in', '')
        time_out = dealer_answer_dict.get('time_out', '')
        if time_in and time_out:
            time_delta = time_out - time_in
            time_visit = gettime(time_delta, format="%H:%M:%S")
        time_in = gettime(time_in)
        time_out = gettime(time_out)

        region_rank = dealer_answer_dict.get('region_rank', '')
        nation_rank = dealer_answer_dict.get('nation_rank', '')

    #经销商得分与区域/全国得分对比
    barData = []
    lineData = []
    lineData2 = []
    chp_list = ['score', 'A', 'B', 'C', 'D', 'E', 'G']
    for cp in chp_list:
        barData.append(dealer_score_dict.get(cp, 0))
        lineData.append(region_score_dict.get(cp, 0))
        lineData2.append(nation_score_dict.get(cp, 0))

    title = ''
    labels = [u'总得分\nTotal Score', u'预约\nAppointment\nscheduling', u'接车&检查车辆\nVehicle Drop-off &\nChecking', u'提车\nVehicle Pick-up', u'账单及付款\nBilling', u'送别客户\nFarewell', "中国区问题\nChinese Specific\nQuestions"]
    img_name = 'chart_dealer_vs_%s.png' % (dealer.id)
    save_as = os.path.join(settings.SITE_ROOT, 'static', 'mcview', 'images', 'chart', img_name)
    data = create_bar_line_xychart(title, labels, barData, lineData, lineData2, mark_value=None, format='{value|1}', fontAngle=0, x=900, y=340, swapxy=False, Scale=100, legendVertical=False)
    file(save_as, 'wb').write(data)


    cp_answer_list = ['Q7c', 'Q34c', 'Q44c', 'Q62', 'Q63', 'Q64']
    cp_score_list = ['Q4a', 'Q7a', 'Q8a', 'Q9a', 'Q11a', 'Q12a', 'Q13a', 'Q16a', 'Q34a', 'Q35a', 'Q43a', 'Q44a', 'Q46a']
    cp_no_score_list = ['Q4b', 'Q4c', 'Q4d', 'Q4e', 'Q7b', 'Q8b', 'Q9b', 'Q11b', 'Q12b', 'Q12c', 'Q12d', 'Q12e', 'Q12f', 'Q12g', 'Q12h', 'Q12i', 'Q13b', 'Q13c', 'Q13d', 'Q16b', 'Q16c', 'Q16d', 'Q34b', 'Q35b', 'Q35c', 'Q43b', 'Q43c', 'Q44b', 'Q46b']
    cp_score_dict = {'Q4a':5, 'Q7a':2, 'Q8a':2, 'Q9a':2, 'Q11a':2, 'Q12a':9, 'Q13a':4, 'Q16a':4, 'Q34a':2, 'Q35a':3, 'Q43a':3, 'Q44a':2, 'Q46a':2}
    green_list = ['Q3',
                  'Q7a', 'Q7b', 'Q7c',
                  'Q12a', 'Q12b', 'Q12c', 'Q12d', 'Q12e', 'Q12f', 'Q12g', 'Q12h', 'Q12i',
                  'Q13a', 'Q13b', 'Q13c', 'Q13d',
                  'Q21',
                  'Q34a', 'Q34b', 'Q34c',
                  'Q44a', 'Q44b', 'Q44c',
                  'Q47', 'Q49', 'Q54', 'Q56', 'Q57', 'Q60', 'Q61', 'Q62', 'Q63', 'Q64']
    if current_term.id == 5:
        cp_answer_list = ['Q7c', 'Q34c', 'Q44c', 'Q61', 'Q62', 'Q63']
        cp_score_list = ['Q4a', 'Q7a', 'Q8a', 'Q9a', 'Q11a', 'Q12a', 'Q13a', 'Q16a', 'Q34a', 'Q35a', 'Q43a', 'Q44a', 'Q46a']
        cp_no_score_list = ['Q4b', 'Q4c', 'Q4d', 'Q4e', 'Q7b', 'Q8b', 'Q9b', 'Q11b', 'Q12b', 'Q12c', 'Q12d', 'Q12e', 'Q12f', 'Q12g', 'Q12h', 'Q12i', 'Q13b', 'Q13c', 'Q13d', 'Q16b', 'Q16c', 'Q16d', 'Q34b', 'Q35b', 'Q35c', 'Q43b', 'Q43c', 'Q44b', 'Q46b']
        cp_score_dict = {'Q4a':5, 'Q7a':2, 'Q8a':2, 'Q9a':2, 'Q11a':2, 'Q12a':9, 'Q13a':4, 'Q16a':4, 'Q34a':2, 'Q35a':3, 'Q43a':3, 'Q44a':2, 'Q46a':2}
        green_list = ['Q3',
                      'Q7a', 'Q7b', 'Q7c',
                      'Q12a', 'Q12b', 'Q12c', 'Q12d', 'Q12e', 'Q12f', 'Q12g', 'Q12h', 'Q12i',
                      'Q13a', 'Q13b', 'Q13c', 'Q13d',
                      'Q21',
                      'Q34a', 'Q34b', 'Q34c',
                      'Q44a', 'Q44b', 'Q44c',
                      'Q47', 'Q49', 'Q53', 'Q55', 'Q56', 'Q59', 'Q60', 'Q61', 'Q62', 'Q63']
    cp_part1_list = []
    cp_part2_list = []
    for i, sub_cp in enumerate(sub_cp_list):
        if sub_cp.name in green_list:
            cp_part2_list.append(sub_cp)
        else:
            cp_part1_list.append(sub_cp)

        sub_cp.dealer_answer = dealer_answer_dict.get(sub_cp.name)
        sub_cp.dealer_score = dealer_score_dict.get(sub_cp.name)
        sub_cp.region_score = region_score_dict.get(sub_cp.name)
        sub_cp.nation_score = nation_score_dict.get(sub_cp.name)

        if sub_cp.name in cp_score_list:
            sub_cp.rowspan = cp_score_dict.get(sub_cp.name)
            sub_cp.dealer_score = dealer_score_dict.get(sub_cp.name[:-1])
            sub_cp.region_score = region_score_dict.get(sub_cp.name[:-1])
            sub_cp.nation_score = nation_score_dict.get(sub_cp.name[:-1])

        if sub_cp.dealer_score is None or sub_cp.dealer_score == -999 or sub_cp.dealer_score == '/':
            sub_cp.dealer_score = '/'
            sub_cp.compare_region = '-'
            sub_cp.compare_nation = '-'

            if sub_cp.region_score is None or sub_cp.region_score == '/':
                sub_cp.region_score = '-'
            else:
                sub_cp.region_score = '%.1f' % (sub_cp.region_score or 0)

            if sub_cp.nation_score is None or sub_cp.nation_score == '/':
                sub_cp.nation_score = '-'
            else:
                sub_cp.nation_score = '%.1f' % (sub_cp.nation_score or 0)

#            if sub_cp.xq_score is None:
#                sub_cp.xq_score = '-'
#            else:
#                sub_cp.xq_score = '%.1f' % (sub_cp.xq_score or 0)
#                
#            if sub_cp.city_score is None:
#                sub_cp.city_score = '-'
#            else:
#                sub_cp.city_score = '%.1f' % (sub_cp.city_score or 0)
#                
#            if sub_cp.province_score is None:
#                sub_cp.province_score = '-'
#            else:
#                sub_cp.province_score = '%.1f' % (sub_cp.province_score or 0)
#                
#            if sub_cp.jt_score is None:
#                sub_cp.jt_score = '-'
#            else:
#                sub_cp.jt_score = '%.1f' % (sub_cp.jt_score or 0)
        else:
            try:
                region_has_score = isinstance(sub_cp.region_score, (int, float))
            except:
                region_has_score = False
            if region_has_score:
#                print sub_cp,sub_cp.dealer_score
                sub_cp.compare_region = sub_cp.dealer_score - (sub_cp.region_score or 0)
                sub_cp.region_score = '%.1f' % (sub_cp.region_score or 0)
                sub_cp.compare_region = '%.1f' % sub_cp.compare_region
            else:
                sub_cp.compare_region = '-'
                sub_cp.region_score = '-'

            try:
                nation_has_score = isinstance(sub_cp.nation_score, (int, float))
            except:
                nation_has_score = False
            if nation_has_score:
                sub_cp.compare_nation = sub_cp.dealer_score - (sub_cp.nation_score or 0)
                sub_cp.nation_score = '%.1f' % (sub_cp.nation_score or 0)
                sub_cp.compare_nation = '%.1f' % sub_cp.compare_nation
            else:
                sub_cp.nation_score = '-'

#            if sub_cp.xq_score and isinstance(sub_cp.xq_score,(int, float)):
#                sub_cp.compare_xq = sub_cp.dealer_score - (sub_cp.xq_score or 0)
#                sub_cp.xq_score = '%.1f' % (sub_cp.xq_score or 0)
#                sub_cp.compare_xq = '%.1f' % sub_cp.compare_xq
#            else:
#                sub_cp.compare_xq = '-'
#                sub_cp.xq_score = '-'
#                
#            if sub_cp.city_score and isinstance(sub_cp.city_score,(int, (int, float))):
#                sub_cp.compare_city = sub_cp.dealer_score - (sub_cp.city_score or 0)
#                sub_cp.city_score = '%.1f' % (sub_cp.city_score or 0)
#                sub_cp.compare_city = '%.1f' % sub_cp.compare_city
#            else:
#                sub_cp.compare_city = '-'
#                sub_cp.city_score = '-'
#                
#            if sub_cp.province_score and isinstance(sub_cp.province_score,(int, (int, float))):
#                sub_cp.compare_province = sub_cp.dealer_score - (sub_cp.province_score or 0)
#                sub_cp.province_score = '%.1f' % (sub_cp.province_score or 0)
#                sub_cp.compare_province = '%.1f' % sub_cp.compare_province
#            else:
#                sub_cp.compare_province = '-'
#                sub_cp.province_score = '-'
#                
#            if sub_cp.jt_score and isinstance(sub_cp.jt_score,(int, float)):
#                sub_cp.compare_jt = sub_cp.dealer_score - (sub_cp.jt_score or 0)
#                sub_cp.jt_score = '%.1f' % (sub_cp.jt_score or 0)
#                sub_cp.compare_jt = '%.1f' % sub_cp.compare_jt
#            else:
#                sub_cp.compare_jt = '-'
#                sub_cp.jt_score = '-'
            if current_term.id == 5:
                if sub_cp.name not in ('Q7c', 'Q34c', 'Q44c', 'Q61', 'Q62', 'Q63'):
                    sub_cp.dealer_score = '%.1f' % sub_cp.dealer_score
                else:
                    tmps = sub_cp.dealer_score
                    sub_cp.dealer_score = tmps
            else:
                if sub_cp.name not in ('Q7c', 'Q34c', 'Q44c', 'Q62', 'Q63', 'Q64'):
                    sub_cp.dealer_score = '%.1f' % sub_cp.dealer_score
                else:
                    tmps = sub_cp.dealer_score
                    sub_cp.dealer_score = tmps
        if sub_cp.name == 'G64':
            if str(sub_cp.dealer_score) == '0.0' or str(sub_cp.dealer_score) == '不适用':
                sub_cp.dealer_score = u'否<br>No'
            elif str(sub_cp.dealer_score) == '100.0':
                sub_cp.dealer_score = u'是<br>Yes'
            if str(sub_cp.region_score) == '0.0'  or str(sub_cp.region_score) == '不适用':
                sub_cp.region_score = u'否<br>No'
            elif str(sub_cp.region_score) == '100.0':
                sub_cp.region_score = u'是<br>Yes'
            if str(sub_cp.nation_score) == '0.0' or str(sub_cp.nation_score) == '不适用':
                sub_cp.nation_score = u'否<br>No'
            elif str(sub_cp.nation_score) == '100.0':
                sub_cp.nation_score = u'是<br>Yes'
            if str(sub_cp.xq_score) == '0.0' or str(sub_cp.xq_score) == '不适用':
                sub_cp.xq_score = u'否<br>No'
            elif str(sub_cp.xq_score) == '100.0':
                sub_cp.xq_score = u'是<br>Yes'
            if str(sub_cp.city_score) == '0.0' or str(sub_cp.city_score) == '不适用':
                sub_cp.city_score = u'否<br>No'
            elif str(sub_cp.city_score) == '100.0':
                sub_cp.city_score = u'是<br>Yes'
            if str(sub_cp.province_score) == '0.0' or str(sub_cp.province_score) == '不适用':
                sub_cp.province_score = u'否<br>No'
            elif str(sub_cp.province_score) == '100.0':
                sub_cp.xq_score = u'是<br>Yes'
            if str(sub_cp.jt_score) == '0.0' or str(sub_cp.jt_score) == '不适用':
                sub_cp.jt_score = u'否<br>No'
            elif str(sub_cp.jt_score) == '100.0':
                sub_cp.jt_score = u'是<br>Yes'

    data_version = settings.DATA_VERSION

    return locals()

@login_required
def history_now_future_report(request, paper_id):
    paper = _paper.get_paper(id=int(paper_id))
    term = paper.term
    if paper is None:
        return locals()
    dealer = paper.dealer
    term_list = map(copy.copy, _term.get_all_terms())
    if paper.visit_end and paper.visit_begin:
        paper.visit_minutes = (paper.visit_end - paper.visit_begin).seconds / 60
    else:
        paper.visit_minutes = 0
    cp_group_list, cp_total = make_hnf_dealer_charts(term_list, paper.project.id, dealer, dealer.dealertype, paper.paper_type)

    data_version = settings.DATA_VERSION

    filename = u'%s_%s_%s_历史现在未来报告.xls' % (term.name, dealer.name_cn, dealer.name)
    filepath = os.path.join(settings.MEDIA_ROOT, 'hnf_report', filename)
    fileurl = ''
    if os.path.exists(filepath):
        fileurl = u'/file/%s/%s' % ('hnf_report', filename)

    return locals()

def sort_by_name(cp):
    """A2 return A02"""
    return '%s%s' % (cp.name_abbr[0], cp.name_abbr[1:].zfill(2))

def make_term_compare_chart(term_list, dealer):
    title = u'各期数得分对比'
    labels = [u'%s/%s' % (term.name_cn, term.name_en) for term in term_list]
    data = [term.dealer_score for term in term_list]

    img_name = 'chart_compare_%s.png' % (dealer.id)
    save_as = os.path.join(settings.SITE_ROOT, 'static', 'mcview', 'images', 'chart', img_name)
    data = create_simple_xychart(title, labels, data)
    file(save_as, 'wb').write(data)
    return img_name

def make_hnf_dealer_charts(term_list, project_id, dealer, dealertype, paper_type):
    title = '经销商总得分Total Score'
    labels = ['2011', '2012', ]

    project = _project.get_project_id_map()[project_id]
    paper_type = enums.BMW_PAPER_TYPE
    for term in term_list:
        #labels.append(' % s /% s' % (term.name_cn, term.name_en))
        #~ print term.id,dealer.name_cn
        tmp_project_id = project_id
        if term.id <= 4:
            tmp_project_id = 1
            paper_type = enums.FW_PAPER_TYPE
        else:
            paper_type = enums.BMW_PAPER_TYPE
            if tmp_project_id == constant.competition_project_id:
                paper_type = enums.FW_PAPER_TYPE
        protmp = _project.get_project_id_map()[tmp_project_id]
        cp_name_list = _checkpoint.get_project_cp_name_list_with_total(protmp)
        score_list_dealer = _report.get_dealer_score(term, dealer, protmp, dealertype, paper_type, cp_name_list)
        score_dict_dealer = {}
        for i, cp_name in enumerate(cp_name_list):
            if score_list_dealer:
                score_dict_dealer[cp_name] = score_list_dealer[i]
        term.score_dict_dealer = score_dict_dealer

    cp_group_list = map(copy.copy, _checkpoint.get_project_cp_list_with_total(project))
    #cp_group_list.remove(cp_group_list[len(cp_group_list) - 1])
    remove_cp = []
    for i, cp_group in enumerate(cp_group_list):
        if 'G' in cp_group.name_abbr:
            remove_cp.append(cp_group)
            continue
        if cp_group.desc_en and cp_group.has_child:
            title = u'%s%s' % (cp_group.desc.replace('\n', ''), cp_group.desc_en)
        else:
            title = u'%s' % (cp_group.desc.replace('\n', ''))

        W1_list = []
        W2_list = []
        W3_list = []
        W4_list = []

        cur_term = _term.get_all_terms().order_by('-id')[0]
        for tid in range(cur_term.id):
            w = tid % 4
            if w == 0:
                if term_list[tid]:
                    if term_list[tid].score_dict_dealer:
                        try:
                            W1_list.append(term_list[tid].score_dict_dealer[cp_group.name])
                        except:
                            W1_list.append(-1)
                    else:
                        W1_list.append(-1)
            elif w == 1:
                if term_list[tid]:
                    if term_list[tid].score_dict_dealer:
                        try:
                            W2_list.append(term_list[tid].score_dict_dealer[cp_group.name])
                        except:
                            W2_list.append(-1)
                    else:
                        W2_list.append(-1)
            elif w == 2:
                if term_list[tid]:
                    if term_list[tid].score_dict_dealer:
                        try:
                            W3_list.append(term_list[tid].score_dict_dealer[cp_group.name])
                        except:
                            W3_list.append(-1)
                    else:
                        W3_list.append(-1)
            elif w == 3:
                if term_list[tid]:
                    if term_list[tid].score_dict_dealer:
                        try:
                            W4_list.append(term_list[tid].score_dict_dealer[cp_group.name])
                        except:
                            W4_list.append(-1)
                    else:
                        W4_list.append(-1)
            else:
                pass

        series_list = []

        img_name = 'chart_hnf_%s_%s.png' % (i, dealer.id)
        save_as = '%s/static/mcview/images/chart/%s' % (settings.SITE_ROOT, img_name)


        series_list.append(dict(name=u'W1', value=W1_list))
        series_list.append(dict(name=u'W2', value=W2_list))
        series_list.append(dict(name=u'W3', value=W3_list))
        series_list.append(dict(name=u'W4', value=W4_list))

        series_top = {}

        data = create_history_now_future_xychart(title, labels, series_list, series_top)
        file(save_as, 'wb').write(data)
        cp_group.chart_img = img_name
    for rem in remove_cp:
        cp_group_list.remove(rem)
    cp_total = cp_group_list[0]
    cp_group_list = cp_group_list[1:]
    return cp_group_list, cp_total

def make_dealer_charts(term_list, report):
    score_dealer_list = []
    score_region_list = []
    score_nation_list = []
    score_top_list = []

    labels = []

    dealer = report.dealer
    project = report.project
    dealertype = dealer.dealertype
    cp_group_list = map(copy.copy, _checkpoint.get_project_cp_group_list(project.id))
    cp_name_list = [cp.name for cp in cp_group_list]
    for term in term_list:
        dealer_reports = Report.objects.filter(dealertype=dealer.dealertype, term=term, dealer=dealer)
        labels.append('%s/%s' % (term.name_cn, term.name_en))
        #~ print term.id,dealer.name_cn
        dealer_score_dict = {}
        if dealer_reports:
            dealer_report = dealer_reports[0]
            dealer_score_str = dealer_report.score_str
            dealer_score_dict = str_to_pyobj(dealer_score_str)

        report_region_list = Report.objects.filter(dealertype=dealer.dealertype, term=term, dealer=dealer.parent.parent)
        region_score_dict = {}
        if report_region_list:
            report_region = report_region_list[0]
            report_score_str = report_region.score_str
            if report_score_str:
                region_score_dict = str_to_pyobj(report_score_str)

        report_nation_list = Report.objects.filter(dealertype=dealer.dealertype, term=term, dealer__level=0)
        nation_score_dict = {}
        if report_nation_list:
            report_nation = report_nation_list[0]
            nation_score_str = report_nation.score_str
            if nation_score_str:
                nation_score_dict = str_to_pyobj(nation_score_str)

        report_xq_list = Report.objects.filter(dealertype=dealer.dealertype, term=term, dealer=dealer.xq_parent)
        xq_score_dict = {}
        if report_xq_list:
            report_xq = report_xq_list[0]
            xq_score_str = report_xq.score_str
            if xq_score_str:
                xq_score_dict = str_to_pyobj(xq_score_str)

        report_city_list = Report.objects.filter(dealertype=dealer.dealertype, term=term, dealer=dealer.parent)
        city_score_dict = {}
        if report_city_list:
            report_city = report_city_list[0]
            city_score_str = report_city.score_str
            if city_score_str:
                city_score_dict = str_to_pyobj(city_score_str)

        report_province_list = Report.objects.filter(dealertype=dealer.dealertype, term=term, dealer=dealer.sf_parent.sf_parent)
        province_score_dict = {}
        if report_province_list:
            report_province = report_province_list[0]
            province_score_str = report_province.score_str
            if province_score_str:
                province_score_dict = str_to_pyobj(province_score_str)

        report_jt_list = Report.objects.filter(dealertype=dealer.dealertype, term=term, dealer=dealer.jt_parent)
        jt_score_dict = {}
        if report_jt_list:
            report_jt = report_jt_list[0]
            jt_score_str = report_jt.score_str
            if jt_score_str:
                jt_score_dict = str_to_pyobj(jt_score_str)

        term.score_dict_dealer = dealer_score_dict
        term.score_dict_region = region_score_dict
        term.score_dict_nation = nation_score_dict
        term.score_dict_xq = xq_score_dict
        term.score_dict_city = city_score_dict
        term.score_dict_province = province_score_dict
        term.score_dict_jt = jt_score_dict

    for i, cp_group in enumerate(cp_group_list):
#        if cp_group.desc_en:
#            title = u'%s%s' % (cp_group.desc, cp_group.desc_en)
#        else:
#            title = u'%s' % (cp_group.desc)
        title = ''
        score_dealer_list = []
        score_region_list = []
        score_nation_list = []
        score_xq_list = []
        score_city_list = []
        score_province_list = []
        score_jt_list = []

        score_top_list = []
        for term_index, term in enumerate(term_list):
            if None in [term.score_dict_region, term.score_dict_nation, term.score_dict_xq, term.score_dict_city, term.score_dict_province, term.score_dict_jt]:
                if term.score_dict_dealer:
                    s = term.score_dict_dealer.get(cp_group.name, 0)
                else:
                    s = 0
                score_dealer_list.append(s)
            else:
                if term.score_dict_dealer:
                    score_dealer_list.append(term.score_dict_dealer.get(cp_group.name, 0))
                else:
                    score_dealer_list.append(0)

                score_region_list.append(term.score_dict_region.get(cp_group.name, 0))
                score_nation_list.append(term.score_dict_nation.get(cp_group.name, 0))
                score_xq_list.append(term.score_dict_xq.get(cp_group.name, 0))
                score_city_list.append(term.score_dict_city.get(cp_group.name, 0))
                score_province_list.append(term.score_dict_province.get(cp_group.name, 0))
                score_jt_list.append(term.score_dict_jt.get(cp_group.name, 0))

#            score = _report.get_bmw_top_score(term, report, cp_group)
#            #print 'score',score
#            score_top_list.append(score)

        series_list = []

        img_name = 'chart_%s_%s.png' % (i, dealer.id)
        save_as = '%s/static/mcview/images/chart/%s' % (settings.SITE_ROOT, img_name)

        #if [] in [score_region_list,score_nation_list,score_top_list]:
        #    series_list.append(dict(name=u'当前经销商得分', value = score_dealer_list))
        #    series_top = None
        #else:

        series_list.append(dict(name=u'', value=score_dealer_list))
        series_list.append(dict(name=u'全国平均得分 National average score', value=score_nation_list))
        series_list.append(dict(name=u'所属区域平均得分 Regional average score', value=score_region_list))
        series_list.append(dict(name=u'所属小区平均得分 Sub district average score', value=score_xq_list))
        series_list.append(dict(name=u'所属省份平均得分 Province average score', value=score_province_list))
        series_list.append(dict(name=u'所属城市平均得分 City average score', value=score_city_list))
        series_list.append(dict(name=u'所属经销商集团平均得分 Dealer group average score', value=score_jt_list))

        series_top = dict(name=u'全国最佳经销商得分', value=score_top_list)
        series_top = {}
        maxv = 100
#        if cp_group.name == 'G':
#            maxv = 10
        data = create_multi_xychart(title, labels, series_list, series_top, maxv)
        file(save_as, 'wb').write(data)
        cp_group.chart_img = img_name
    return cp_group_list

#为第三期增加4道题
def _add_four_question(sub_cp_list, current_term, dealer, paper):
    from survey.models import Question, CheckPoint
    q1 = Question.objects.get(cid='A52')
    q1.title_en = 'Did the appointment staff inform the estimated time for SRP job and the quotation when making appointment?'

    q2 = Question.objects.get(cid='B53')
    q2.title_en = 'Did the SA introduce the benefit of appointment booking to you?'

    q3 = Question.objects.get(cid='C54')
    q3.title_en = 'Was the customer offerred internet service while waiting?'

    q4 = Question.objects.get(cid='E55')
    q4.title_en = 'Was the customer served by no more than 2 SA/SAA during the whole process?'

    qs = [q1, q2, q3, q4]
    for q in qs:
        ck1 = CheckPoint(question=q)
        ck1.name = q.cid
        ck1.desc = q.title
        ck1.desc_en = q.title_en
        pos = mc.get_pos(sub_cp_list, q.cid)
        sub_cp_list.insert(pos, ck1)

        mc.get_dealer_score_info(dealer, current_term, ck1, paper)

@login_required
def download_report(request, dealer_id, term_id):
    from mc.models import Term
    current_term = Term.objects.get(id=term_id)
    dealer = mc.get_dealer(id=dealer_id)
    try:
        import zipfile, os, cStringIO
        file = cStringIO.StringIO()
        data = zipfile.ZipFile(file, 'w', zipfile.ZIP_DEFLATED)
        target_file_name = u'report/%s/%s/%s/%s/%s_%s_%s_%s_报告.xls' % (current_term.id, dealer.dealertype.name_cn, dealer.parent.parent.name_cn, dealer.province_cn, dealer.name, dealer.dealertype.name_cn, dealer.abbr_cn, current_term.name)
        path = os.path.join(settings.MEDIA_ROOT, target_file_name)
        arcname = os.path.basename(unicode(path))
        arcname = '%s_%s_%s_%s' % (dealer.name_cn, dealer.name, dealer.dealertype.name_cn, current_term.name_en)
        if current_term.is_finished:
            from datetime import datetime
            nowday = datetime.today()
            arcname += '_%d%d%d' % (nowday.year, nowday.month, nowday.day)
        arcname += '.xls'

        data.write(path, arcname.encode('gb18030'))
        data.close()
    except:
        return HttpResponse(u'找不到文件！')

    if data:
        response = HttpResponse(file.getvalue(), mimetype='application/x-zip-compressed')
        data.close()
        response['Content-Disposition'] = (u'attachment; filename=report.zip').encode('utf-8')
        return response

@login_required
def dealerLogin(request):
    current_term = _term.get_cur_input_term()

    import DbUtils   #自定义了一个封装connection的models
    try:
        c, con = DbUtils.cursor()
        sql = 'select d.name_cn, d.name_en,username,p.login_count,last_login  from auth_user_groups a,auth_user u,mc_dealer d,userpro_userprofile p,userpro_userprofile_user_permissions pp where p.user_id=u.id and a.user_id=u.id and a.group_id=%d and u.username=d.name and d.has_child=0 and pp.userpermission_id=%d  and pp.userprofile_id = p.id' % (1, 16)
        c.execute(sql)
        tmp1 = c.fetchall()
        dealer_login_info = []
        dealer_login_info.extend(tmp1)
        sql = 'select d.name_cn, d.name_en,username,p.login_count,last_login  from auth_user_groups a,auth_user u,mc_dealer d,userpro_userprofile p,userpro_userprofile_user_permissions pp where p.user_id=u.id and a.user_id=u.id and a.group_id=%d and d.name= "35649_M" and  u.username="35649" and d.has_child=0 and pp.userpermission_id=%d  and pp.userprofile_id = p.id' % (1, 16)
        c.execute(sql)
        tmp2 = c.fetchall()
        dealer_login_info.extend(tmp2)
    finally:
        if c:
            c.close()
        if con:
            con.close()
    return locals()

@login_required
def papers_compare(request):
    checks = request.COOKIES.get('checks', '')
    report_ids = checks.split('%2C')
    dealer_group_score_dict = {}
    dealer_list = []
    ds_score_dict = {}
    dealer_report_dict = {}
    reports = Report.objects.filter(id__in=report_ids)

    if reports:
        checkpoint_list = _report.get_main_group_score_column_str(reports[0].project)
        checkpoint_group_list = ['score']
        checkpoint_group_list.extend([cp.name for cp in checkpoint_list])

        for report in reports:
            dealer_list.append(report.dealer)
            score_dict = {}
            score_str = report.score_str
            if score_str:
                score_dict = str_to_pyobj(score_str)

            cp_score_list = []
            for cp in checkpoint_group_list:
                cp_score_list.append(score_dict.get(cp))
            dealer_group_score_dict[report.dealer] = cp_score_list
            dealer_sub_score = score_dict
            ds_score_dict[report.dealer] = dealer_sub_score
            dealer_report_dict[report.dealer] = report

        #按dealer.id排序，确保环节与检查点显示的是一致的
        dealer_list.sort(sortfunc)
        sub_checkpoint_list = map(copy.copy, _checkpoint.get_sub_checkpoint_list(report.project.id))

        dealer_sub_score_list = []
        for i, sub_cp in enumerate(sub_checkpoint_list):
            scores = []
            for dealer in dealer_list:
                score = ds_score_dict[dealer].get(sub_cp.name)
                report = dealer_report_dict[dealer]
                if score == 0:
                    zero_reason, zero_reason_en = _question.get_zero_reason(report, sub_cp)
                elif score is None:
                    score = '不适用'
                    zero_reason = '-'
                    zero_reason_en = '-'
                    zero_reason, zero_reason_en = _question.get_zero_reason(report, sub_cp)
                else:
                    if isinstance(score, float):
                        score = '%.1f' % score
                    zero_reason = '-'
                    zero_reason_en = '-'
                scores.append({'score':score, 'zero_reason':zero_reason, 'zero_reason_en':zero_reason_en})
            dealer_sub_score_list.append((sub_cp, scores))
        dealer_group_score_dict = dict(sorted(dealer_group_score_dict.items(), key=lambda d: d[0].id))

    return locals()

@login_required
def downloadreports(request):
    if request.method == "POST":
        checks = request.COOKIES.get('checks', '')
        report_ids = checks.split('%2C')
        if report_ids:
            report_list = Report.objects.filter(id__in=report_ids)
            dealer_list = [report.dealer for report in report_list]
            if report_list:
                current_term = report_list[0].term
            #current_term = _term.get_cur_term()

            try:
                import zipfile, os, cStringIO
                file = cStringIO.StringIO()
                data = zipfile.ZipFile(file, 'w', zipfile.ZIP_DEFLATED)
                for dealer in dealer_list:
                    target_file_name = u'report/%s/%s/%s/%s/%s_%s_%s_%s_报告.xls' % (current_term.id, dealer.dealertype.name_cn, dealer.parent.parent.name_cn, dealer.province_cn, dealer.name, dealer.dealertype.name_cn, dealer.abbr_cn, current_term.name)
                    path = os.path.join(settings.MEDIA_ROOT, target_file_name)
                    arcname = os.path.basename(unicode(path))
                    arcname = '%s_%s_%s_%s' % (dealer.name_cn, dealer.dealertype.name_cn, dealer.name, current_term.name_en)
                    if current_term.is_finished:
                        from datetime import datetime
                        nowday = datetime.today()
                        arcname += '_%d%d%d' % (nowday.year, nowday.month, nowday.day)
                    arcname += '.xls'
                    data.write(path, arcname.encode('gb18030'))
                data.close()
            except:
                return HttpResponse(u'找不到文件！')
            if data:
                response = HttpResponse(file.getvalue(), mimetype='application/x-zip-compressed')
                data.close()
                response['Content-Disposition'] = (u'attachment; filename=reports.zip').encode('utf-8')
                return response

@login_required
def all_filter(request, kind):
    terms = _term.get_list_terms(_term.get_cur_term())
    dealertypes = _dealer.get_dealer_types()
    kind_id = kind
    if kind_id == 'newold':
        dealertypes = dealertypes.filter(id=1)
    item_cn = constant.data_compare_dict[kind_id]
    item_en = constant.data_compare_en_dict[kind_id]
    return locals()

@login_required
def ajax_all_filter(request):
    term_id = int(request.POST.get('Term', 0))
    dealertype_id = int(request.POST.get('Wave', 0))
    kind = request.POST.get('kind', None)
    if kind:
        if kind == 'user':
            col1 = u'<strong>访问员ID</strong><br>Auditor ID'
            col2 = u'<strong>走访经销商数量</strong><br>No. of Dealers'
        if kind == 'num':
            col1 = u'<strong>进店人数</strong><br>No. of visitor'
            col2 = u'<strong>经销商数量</strong><br>No. of Dealers'
        if kind == 'newold':
            col1 = u'<strong>新店和老店</strong><br>Old & new dealer'
            col2 = u'<strong>经销商数量</strong><br>No. of Dealers'
        items = _report.get_otherreport(kind, term_id, dealertype_id)

    project_id = constant.dealertype_id_to_project_id(dealertype_id)
    project = _project.get_project_by_id(project_id)
    cp_list = _checkpoint.get_project_cp_list_with_total(project)
    cp_list = sort_cp_list(cp_list)

    return locals()

@login_required
def otherreport_compare(request):
    rep_ids = [str(req) for req in request.POST.getlist('item')]
    cplist = [str(cpl) for cpl in request.POST.getlist('cplist')]
    kind = request.POST.get('kind')
    item_name = constant.data_compare_dict[kind]
    item_name_en = constant.data_compare_en_dict[kind]
    project_id = int(request.POST.get('project', 0))
    project = _project.get_project_by_id(project_id)
    if 'all' in cplist:
        cp_list = _checkpoint.get_project_cp_list_with_total(project)
    else:
        cp_list = _checkpoint.get_cp_list_by_name(cplist, project)
    cp_list = sort_cp_list(cp_list)

    item_group_score_dict = {}
    item_sub_score_dict = {}
    ds_score_dict = {}
    item_list = []
    total = CheckPoint()
    total.name = 'total'
    total.name_abbr = 'Total'
    total.desc = u'总得分'
    total.desc_en = 'Total Score'
    cp_name_group_list = ['total', ]
    checkpoint_group_list = [total, ]
    sub_checkpoint_list = []
    cp_dict = _checkpoint.get_question_checkpoint_dict(project)
    for cp in cp_list:
        if cp.name not in cp_name_group_list :
            if cp.has_child:
                cp_name_group_list.append(cp.name)
                checkpoint_group_list.append(cp_dict[cp.name])
            else:
                sub_checkpoint_list.append(cp.name)

    reports = OtherReport.objects.filter(id__in=rep_ids)
    for rep in reports:
        if kind == 'user':
            item = rep.user.first_name
        if kind == 'num':
            item = u'%d人' % rep.visitor_num
        if kind == 'newold':
            if rep.newold:
                item = u'新店<br> New dealer'
            else:
                item = u'老店<br> Old dealer'
        item_list.append(item)
        item_group_score_dict[item] = _report.get_otherreport_group_score_0(rep.id, ','.join(cp_name_group_list))
        ds_score_dict[item] = _report.get_otherreport_sub_score(rep.id, project.id)

    item_list.sort()
    for i, cp_name in enumerate(sub_checkpoint_list):
        sub_cp = cp_dict[cp_name]
        item_sub_score_dict[sub_cp] = []
        for item in item_list:
            score = ds_score_dict[item][i]
            if score == 0 or score is not None:
                score = '%.1f' % score
            else:
                score = u'不适用'
            item_sub_score_dict[sub_cp].append(score)
    has_sub_checkpoint = len(item_sub_score_dict) > 0
    item_group_score_dict = sorted(item_group_score_dict.items(), key=lambda t: t[0])
    return locals()

@login_required
def details(request, search_type, term_id, project_id, search_item, dealer_type):
    stype = search_type
    dtype = dealer_type
    item = search_item
    term = _term.get_term_by_id(term_id)
    project = _project.get_project_by_id(project_id)
    cp_list = _checkpoint.get_project_cp_list_with_total(project)
    cp_list = sort_cp_list(cp_list)
    return locals()

def sort_cp_list(cp_list):
    temp_list = []
    for cp in cp_list:
        if cp.has_child:
            temp_list.append(cp)
    for cp in cp_list:
        if not cp.has_child:
            temp_list.append(cp)
    return temp_list

@login_required
def ajax_get_details(request):
    stype = request.POST.get('search_type', None)
    item = request.POST.get('search_item', None)
    project_id = request.POST.get('project_id', None)
    term_id = request.POST.get('term_id', None)
    dealer_type = request.POST.get('dealer_type', None)
    project = _project.get_project_by_id(project_id)
    term = _term.get_term_by_id(term_id)
    cplist = request.POST.getlist('cplist')
    if 'all' in cplist:
        cp_list = _checkpoint.get_project_cp_list_with_total(project)
        cp_list = sort_cp_list(cp_list)
    else:
        cp_list = _checkpoint.get_cp_list_by_name(cplist, project)

    #根据类型和数据获得不同的问卷
    papers = _paper.get_papers_by_items(stype, item, project, term, dealer_type)

    _report.set_score_in_papers(cp_list, papers)

    return locals()

@login_required
def advanced_search(request, kind):
    terms = _term.get_list_terms(_term.get_cur_term())
    dealertypes = _dealer.get_dealer_types()
    kind_id = kind
    if kind == constant.data_compare_subdistrict_name or kind == constant.data_compare_dealergroup_name:
        dealertypes = [_dealer.get_dealertype_BMW(), ]
    item_name = constant.data_compare_dict[kind]
    item_name_en = constant.data_compare_en_dict[kind]
    return locals()
@login_required
def ajax_dealer_group_result(request):
    term_id = int(request.POST.get('Term', 0))
    dealertype_id = int(request.POST.get('Wave', 0))
    kind = request.POST.get('kind', constant.data_compare_regional_name)
    item_name = constant.data_compare_dict[kind]
    item_name_en = constant.data_compare_en_dict[kind]
    project_id = constant.dealertype_id_to_project_id(dealertype_id)
    project = _project.get_project_by_id(project_id)
    dealer_level_id = constant.data_compare_kind_dict[kind]
    reports = Report.objects.filter(dealer__level=dealer_level_id, dealertype__id=dealertype_id, project__id=project_id, term__id=term_id)
    cp_list = _checkpoint.get_project_cp_list_with_total(project)
    #MINI问卷无G50题目（开放题）
    if project.id == 3:
        ret = []
        for cp in cp_list:
            if cp.name_abbr == 'G50' or cp.name_abbr == 'G51':
                continue;
            ret.append(cp)
        cp_list = ret
    cp_list = sort_cp_list(cp_list)


    for rep in reports:
        rep.ready = False
        if rep.score != None:
            rep.ready = True
    return locals()
@login_required
def advanced_brand(request):
    terms = _term.get_list_terms(_term.get_cur_term())
    kind_id = constant.data_compare_brand_name
    item_name = constant.data_compare_dict[kind_id]
    item_name_en = constant.data_compare_en_dict[kind_id]
    return locals()

@login_required
def ajax_brand_result(request):
    term_id = int(request.POST.get('Term', 0))
    kind = request.POST.get('kind', constant.data_compare_regional_name)
    item_name = constant.data_compare_dict[kind]
    item_name_en = constant.data_compare_en_dict[kind]
#    dealer_level_id = constant.data_compare_kind_dict[kind]
#    reports = Report.objects.filter(dealer__level=dealer_level_id, term__id=term_id)
    national = Dealer.objects.get(pk=1)
    dealers = [national, ]
    areas = Dealer.objects.filter(parent=national, level=1)
    dealers.extend(areas)

    reports = Report.objects.filter(dealer__in=dealers, term__id=term_id)

    cp_list = _checkpoint.get_brand_compare_cp_list()
    cp_list = sort_cp_list(cp_list)

    for rep in reports:
        rep.ready = False
        if rep.score != None:
            rep.ready = True
    return locals()

@login_required
def history_now_future_group_report(request, kind, report_id):
    rep = Report.objects.get(pk=report_id)
    if rep is None:
        return locals()
    term = rep.term
    dealer = rep.dealer
    dealertype = rep.dealertype
    project = rep.project
    paper_type = rep.paper_type
    term_list = map(copy.copy, _term.get_all_terms())
    item_name = constant.data_compare_dict[kind]
    item_name_en = constant.data_compare_en_dict[kind]
    cp_group_list, cp_total = make_hnf_dealer_charts(term_list, project.id, dealer, dealertype, paper_type)
    data_version = settings.DATA_VERSION

    filename = u'%s_%s_%s_%s_历史现在未来报告.xls' % (item_name, term.name, dealer.name_cn, dealertype.name_cn)
    filepath = os.path.join(settings.MEDIA_ROOT, 'hnf_report', filename)
    fileurl = ''
    if os.path.exists(filepath):
        fileurl = u'/file/%s/%s' % ('hnf_report', filename)

    return locals()

class DealerItem():
    pass
@login_required
def items_compare(request):
    rep_ids = [str(req) for req in request.POST.getlist('item')]
    reports = Report.objects.filter(id__in=rep_ids)

    competition = False
    for r in reports:
        if r.project.id == constant.competition_project_id:
            competition = True
            break

    cplist = [str(cpl) for cpl in request.POST.getlist('cplist')]
    kind = request.POST.get('kind')
    item_name = constant.data_compare_dict[kind]
    item_name_en = constant.data_compare_en_dict[kind]

    project_id = request.POST.get('project', 0)
    if project_id:
        project = _project.get_project_by_id(project_id)
        if 'all' in cplist:
            cp_list = _checkpoint.get_project_cp_list_with_total(project)
        else:
            cp_list = _checkpoint.get_cp_list_by_name(cplist, project)
        #MINI问卷无G50题目（开放题）
        if project.id == 3:
            ret = []
            for cp in cp_list:
                if cp.name_abbr == 'G50' or cp.name_abbr == 'G51':
                    continue;
                ret.append(cp)
            cp_list = ret
    else:
        if 'all' in cplist:
            cp_list = _checkpoint.get_brand_compare_cp_list(competition)
        else:
            cp_list = _checkpoint.get_brand_cp_list_by_name(cplist)

    cp_list = sort_cp_list(cp_list)
    dealer_group_score_dict = {}
    ds_score_dict = {}
    dealer_list = []
    cp_name_group_list = ['total', 'max_total', 'min_total']
    checkpoint_group_list = _checkpoint.get_define_cp_total_list()
    sub_checkpoint_list = []
    if project_id:
        cp_dict = _checkpoint.get_question_checkpoint_dict(project)
    else:
        cp_dict = _checkpoint.get_brand_question_checkpoint_dict(competition)
    for cp in cp_list:
        if cp.name not in cp_name_group_list :
            if cp.has_child:
                cp_name_group_list.append(cp.name)
                checkpoint_group_list.append(cp_dict[cp.name])
            else:
                sub_checkpoint_list.append(cp.name)

    for rep in reports:
        dealer = rep.dealer
        dealertype = rep.dealertype
        dealeritem = DealerItem()
        dealeritem.id = rep.id
        dealeritem.name_cn = '%s %s %s' % (dealertype.name_cn, dealer.name_cn, rep.term.name_cn,)
        dealeritem.name_en = '%s %s %s' % (dealertype.name_en, dealer.name_en, rep.term.name_en,)
        dealer_list.append(dealeritem)
        dealer_group_score_dict[dealeritem] = _report.get_report_group_score_0(rep.id, ','.join(cp_name_group_list))
        if project_id:
            ds_score_dict[dealeritem] = _report.get_report_sub_score(rep.id, project.id)
        else:
            if sub_checkpoint_list:
                ds_score_dict[dealeritem] = _report.get_brand_report_sub_score(rep, sub_checkpoint_list)
    #按dealer.id排序，确保环节与检查点显示的是一致的
    dealer_list.sort(sortfunc)
    dealer_sub_score_list = []
    for i, cp_name in enumerate(sub_checkpoint_list):
        sub_cp = cp_dict[cp_name]
        scores = []
        for dealeritem in dealer_list:
            score = ds_score_dict[dealeritem][i]
            if score == 0 or score is not None:
                score = '%.1f' % score
            else:
                score = u'不适用'
            scores.append(score)
        dealer_sub_score_list.append((sub_cp, scores))
    has_sub_checkpoint = len(dealer_sub_score_list) > 0
    dealer_group_score_dict = dict(sorted(dealer_group_score_dict.items(), key=lambda d: d[0].id))
    return locals()

@login_required
def download_history_report(request, dealer_id, term_id):
    #'%s 2012 MS_%s_%s_W%d.xls'%(paper.dealer.dealertype.name_en, paper.dealer.name_cn, paper.dealer.name, paper.term.id % 4)
#    terms = _term.get_2012_all_terms().filter(id__lte=term_id)
    dealer = _dealer.get_dealer(id=dealer_id)

    try:
        import zipfile, os, cStringIO
        file = cStringIO.StringIO()
        data = zipfile.ZipFile(file, 'w', zipfile.ZIP_DEFLATED)

        target_file_name = u'report/11-12年历史报告/%s 单店报告/' % dealer.dealertype.name_cn
        report_dir = os.path.join(settings.MEDIA_ROOT, target_file_name)
        if os.path.isdir(report_dir):
            filenames = os.listdir(report_dir)
            for findfile in filenames:
                if dealer.name in findfile:
                    data.write(os.path.join(report_dir, findfile), findfile)
                    break;

        target_file_name = u'report/13年单店报告/%s report/' % dealer.dealertype.name_cn
        report_dir = os.path.join(settings.MEDIA_ROOT, target_file_name)
        if os.path.isdir(report_dir):
            filenames = os.listdir(report_dir)
            for findfile in filenames:
                if dealer.name in findfile:
                    data.write(os.path.join(report_dir, findfile), findfile)
                    break;

        data.close()
    except:
        return HttpResponse(u'找不到文件！')
    if data:
        response = HttpResponse(file.getvalue(), mimetype='application/x-zip-compressed')
        data.close()
        response['Content-Disposition'] = (u'attachment; filename=%s_history_reports.zip' % dealer.name).encode('utf-8')
        return response

@login_required
def ajax_gen_compare_excel(request):
    rep_ids = request.POST.get('rep_ids').split(',')
    reports = Report.objects.filter(id__in=rep_ids)

    competition = False
    for r in reports:
        if r.project.id == constant.competition_project_id:
            competition = True
            break

    cplist = request.POST.get('cplist').split(',')
    kind = request.POST.get('kind')
    item_name = constant.data_compare_dict[kind]
    item_name_en = constant.data_compare_en_dict[kind]
    user = request.user
    project_id = int(request.POST.get('project_id', 0))
    if project_id:
        project = _project.get_project_by_id(project_id)
        if 'all' in cplist:
            cp_list = _checkpoint.get_project_cp_list_with_total(project)
        else:
            cp_list = _checkpoint.get_cp_list_by_name(cplist, project)
        #MINI问卷无G50题目（开放题）
        if project.id == 3:
            ret = []
            for cp in cp_list:
                if cp.name_abbr == 'G50' or cp.name_abbr == 'G51':
                    continue;
                ret.append(cp)
            cp_list = ret
    else:
        if 'all' in cplist:
            cp_list = _checkpoint.get_brand_compare_cp_list(competition)
        else:
            cp_list = _checkpoint.get_brand_cp_list_by_name(cplist)

    cp_list = sort_cp_list(cp_list)
    dealer_group_score_dict = {}
    ds_score_dict = {}
    dealer_list = []
    cp_name_group_list = ['total', 'max_total', 'min_total']
    checkpoint_group_list = _checkpoint.get_define_cp_total_list()
    sub_checkpoint_list = []
    if project_id:
        cp_dict = _checkpoint.get_question_checkpoint_dict(project)
    else:
        cp_dict = _checkpoint.get_brand_question_checkpoint_dict(competition)
    for cp in cp_list:
        if cp.name not in cp_name_group_list :
            if cp.has_child:
                cp_name_group_list.append(cp.name)
                checkpoint_group_list.append(cp_dict[cp.name])
            else:
                sub_checkpoint_list.append(cp.name)


    for rep in reports:
        dealer = rep.dealer
        dealertype = rep.dealertype
        dealeritem = DealerItem()
        dealeritem.id = rep.id
        dealeritem.name_cn = '%s %s %s' % (dealertype.name_cn, dealer.name_cn, rep.term.name_cn,)
        dealeritem.name_en = '%s %s %s' % (dealertype.name_en, dealer.name_en, rep.term.name_en,)
        dealer_list.append(dealeritem)
        dealer_group_score_dict[dealeritem] = _report.get_report_group_score_0(rep.id, ','.join(cp_name_group_list))
        if project_id:
            ds_score_dict[dealeritem] = _report.get_report_sub_score(rep.id, project.id)
        else:
            if sub_checkpoint_list:
                ds_score_dict[dealeritem] = _report.get_brand_report_sub_score(rep, sub_checkpoint_list)
    #按dealer.id排序，确保环节与检查点显示的是一致的
    dealer_list.sort(sortfunc)
    dealer_sub_score_list = []
    for i, cp_name in enumerate(sub_checkpoint_list):
        sub_cp = cp_dict[cp_name]
        scores = []
        for dealeritem in dealer_list:
            score = ds_score_dict[dealeritem][i]
            if score == 0 or score is not None:
                score = '%.1f' % score
            else:
                score = u'不适用'
            scores.append(score)
        dealer_sub_score_list.append((sub_cp, scores))
    has_sub_checkpoint = len(dealer_sub_score_list) > 0
    dealer_group_score_dict = dict(sorted(dealer_group_score_dict.items(), key=lambda d: d[0].id))

    #生成excel
    source_file_name = u'datacompare/数据对比模板.xls'
    source_file_name = os.path.join(settings.RESOURCES_ROOT, source_file_name)
    filename = u'%s数据对比报告(%s).xls' % (item_name, user.username)
    target_file_name = os.path.join(settings.MEDIA_ROOT, filename)
    file_url = os.path.join(settings.MEDIA_URL, filename)
    excel = easyExcel(source_file_name)
    try:
        data_sheet = 'sheet1'
        excel.setSheetName(data_sheet, u'%s数据对比' % item_name)
        data_sheet = u'%s数据对比' % item_name
        ans = u'对比查看%s售后服务表现 %s after-sales service performance comparison' % (item_name, item_name_en)
        excel.setRangeVal(data_sheet, 'A1', ans)
        ans = u'%s名称' % item_name
        excel.setRangeVal(data_sheet, 'A3', ans)
        ans = u'Aftersales %s Name' % item_name_en
        excel.setRangeVal(data_sheet, 'A4', ans)
        col_list = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']
        for index, group in enumerate(checkpoint_group_list):
            ans = '%s %s' % (group.name_abbr or '', group.desc)
            excel.setRangeVal(data_sheet, '%s3' % col_list[index + 1], ans)
            ans = '%s' % group.desc_en
            excel.setRangeVal(data_sheet, '%s4' % col_list[index + 1], ans)
        row = 5
        for dealer, dealer_score in dealer_group_score_dict.items():
            ans = '%s %s' % (dealer.name_cn, dealer.name_en)
            excel.setRangeVal(data_sheet, '%s%s' % (col_list[0], row), ans)
            for index, score in enumerate(dealer_score):
                excel.setRangeVal(data_sheet, '%s%s' % (col_list[index + 1], row), round(score, 1))
            row += 1
        end_row = row

        if has_sub_checkpoint:
            for index, dealer in enumerate(dealer_list):
                col = get_char(index + 2)
                excel.setRangeVal(data_sheet, '%s%s' % (col, 148), dealer.name_cn)
                excel.setRangeVal(data_sheet, '%s%s' % (col, 149), dealer.name_en)
            row = 150
            for cp, result in dealer_sub_score_list:
                ans = '%s.%s' % (cp.name_abbr, cp.desc)
                excel.setRangeVal(data_sheet, '%s%s' % ('A', row), ans)
                ans = '%s' % cp.desc_en
                excel.setRangeVal(data_sheet, '%s%s' % ('B', row), ans)
                for index, score in enumerate(result):
                    col = get_char(index + 2)
                    ans = score
                    if cp.name_abbr == 'G51':
                        ans = u'%s%s(yes)' % (score, '%')
                    excel.setRangeVal(data_sheet, '%s%s' % (col, row), ans)
                row += 1

        del_row_num = 145 - end_row
        for i in range(del_row_num):
            excel.deleteRow(data_sheet, 145 - i)

        excel.save(target_file_name)
    finally:
        excel.close()
    download = '%s %s %s %s %s %s' % (rep_ids, cplist, kind, item_name, item_name_en, project_id)
    return HttpResponse(simplejson.dumps({'download':download, 'url':file_url}, ensure_ascii=False))

@login_required
def ajax_gen_other_compare_excel(request):
    rep_ids = request.POST.get('rep_ids').split(',')
    cplist = request.POST.get('cplist').split(',')
    kind = request.POST.get('kind')
    item_name = constant.data_compare_dict[kind]
    item_name_en = constant.data_compare_en_dict[kind]
    user = request.user
    project_id = int(request.POST.get('project_id', 0))
    project = _project.get_project_by_id(project_id)
    if 'all' in cplist:
        cp_list = _checkpoint.get_project_cp_list_with_total(project)
    else:
        cp_list = _checkpoint.get_cp_list_by_name(cplist, project)
    cp_list = sort_cp_list(cp_list)

    item_group_score_dict = {}
    item_sub_score_dict = {}
    ds_score_dict = {}
    item_list = []
    total = CheckPoint()
    total.name = 'total'
    total.name_abbr = 'Total'
    total.desc = u'总得分'
    total.desc_en = 'Total Score'
    cp_name_group_list = ['total', ]
    checkpoint_group_list = [total, ]
    sub_checkpoint_list = []
    cp_dict = _checkpoint.get_question_checkpoint_dict(project)
    for cp in cp_list:
        if cp.name not in cp_name_group_list :
            if cp.has_child:
                cp_name_group_list.append(cp.name)
                checkpoint_group_list.append(cp_dict[cp.name])
            else:
                sub_checkpoint_list.append(cp.name)

    reports = OtherReport.objects.filter(id__in=rep_ids)
    for rep in reports:
        if kind == 'user':
            item = rep.user.first_name
        if kind == 'num':
            item = u'%d人' % rep.visitor_num
        if kind == 'newold':
            if rep.newold:
                item = u'新店<br> New dealer'
            else:
                item = u'老店<br> Old dealer'
        item_list.append(item)
        item_group_score_dict[item] = _report.get_otherreport_group_score_0(rep.id, ','.join(cp_name_group_list))
        ds_score_dict[item] = _report.get_otherreport_sub_score(rep.id, project.id)

    item_list.sort()
    for i, cp_name in enumerate(sub_checkpoint_list):
        sub_cp = cp_dict[cp_name]
        item_sub_score_dict[sub_cp] = []
        for item in item_list:
            score = ds_score_dict[item][i]
            if score == 0 or score is not None:
                score = '%.1f' % score
            else:
                score = u'不适用'
            item_sub_score_dict[sub_cp].append(score)
    has_sub_checkpoint = len(item_sub_score_dict) > 0
    item_group_score_dict = sorted(item_group_score_dict.items(), key=lambda t: t[0])

    #生成excel
    source_file_name = u'datacompare/数据对比模板.xls'
    source_file_name = os.path.join(settings.RESOURCES_ROOT, source_file_name)
    filename = u'%s数据对比报告(%s).xls' % (item_name, user.username)
    target_file_name = os.path.join(settings.MEDIA_ROOT, filename)
    file_url = os.path.join(settings.MEDIA_URL, filename)
    excel = easyExcel(source_file_name)
    try:
        data_sheet = 'sheet1'
        excel.setSheetName(data_sheet, u'%s数据对比' % item_name)
        data_sheet = u'%s数据对比' % item_name
        ans = u'%s数据对比 %s Data Comparison' % (item_name, item_name_en)
        excel.setRangeVal(data_sheet, 'A1', ans)
        ans = u'%s名称' % item_name
        excel.setRangeVal(data_sheet, 'A3', ans)
        ans = u'Aftersales %s Name' % item_name_en
        excel.setRangeVal(data_sheet, 'A4', ans)
        col_list = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']
        for index, group in enumerate(checkpoint_group_list):
            ans = '%s %s' % (group.name_abbr or '', group.desc)
            excel.setRangeVal(data_sheet, '%s3' % col_list[index + 1], ans)
            ans = '%s' % group.desc_en
            excel.setRangeVal(data_sheet, '%s4' % col_list[index + 1], ans)
        row = 5
        for item, item_score in item_group_score_dict:
            ans = '%s' % item
            excel.setRangeVal(data_sheet, '%s%s' % (col_list[0], row), ans)
            for index, score in enumerate(item_score):
                excel.setRangeVal(data_sheet, '%s%s' % (col_list[index + 1], row), round(score, 1))
            row += 1
        end_row = row

        if has_sub_checkpoint:
            for index, item in enumerate(item_list):
                col = get_char(index + 2)
                excel.setRangeVal(data_sheet, '%s%s' % (col, 148), item)
                #excel.setRangeVal(data_sheet, '%s%s' % (col, 149), dealer.name_en)
            row = 150
            for cp, result in item_sub_score_dict.items():
                ans = '%s.%s' % (cp.name_abbr, cp.desc)
                excel.setRangeVal(data_sheet, '%s%s' % ('A', row), ans)
                ans = '%s' % cp.desc_en
                excel.setRangeVal(data_sheet, '%s%s' % ('B', row), ans)
                for index, score in enumerate(result):
                    col = get_char(index + 2)
                    ans = score
                    if cp.name_abbr == 'G51':
                        ans = u'%s%s(yes)' % (score, '%')
                    excel.setRangeVal(data_sheet, '%s%s' % (col, row), ans)
                row += 1

        del_row_num = 145 - end_row
        for i in range(del_row_num):
            excel.deleteRow(data_sheet, 145 - i)

        excel.save(target_file_name)
    finally:
        excel.close()
    download = '%s %s %s %s %s %s' % (rep_ids, cplist, kind, item_name, item_name_en, project_id)
    return HttpResponse(simplejson.dumps({'download':download, 'url':file_url}, ensure_ascii=False))

START_COL_NUM = ord('a')
char_list = []
def gen_char_list(index, need_empty=False):
    #index从0开始
    global char_list
    if need_empty:
        char_list = []
    if index < 26:
        char_list.append(chr(index + START_COL_NUM))
    else:
        temp = index / 26 - 1
        char_list.append(chr(index % 26 + START_COL_NUM))
        gen_char_list(temp)

def get_char(index):
    '''获得excel的col字母'''
    gen_char_list(index, need_empty=True)
    char_list.reverse()
    return ''.join(char_list)

def sortfunc(x, y):
        return  cmp(x.id, y.id);
