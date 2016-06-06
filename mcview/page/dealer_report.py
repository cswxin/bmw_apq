#encoding:utf-8
from django.shortcuts import HttpResponseRedirect, Http404, HttpResponse, render_to_response
from mcview.decorator import render_to
from django.contrib.auth.decorators import login_required
from service import dealer_report
from mcview import pageman
from django.conf.urls.defaults import url
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import requires_csrf_token
from django.http import HttpResponseNotFound
from django.utils import simplejson
from mc.models import Dealer
from userpro.models import UserProfile

#经销商单店报告首页
@render_to('index.html')
def index(request):
    return dealer_report.index(request)

#经销商单店报告页面（详细）--无paperid（经销商登录时）
@render_to('dealeranalysis.html')
def dealer_analysis(request):
    return dealer_report.dealer_analysis(request)

#高级数据分析选择页面
@render_to('advancedfilter.html')
def advanced_filter(request):
    return dealer_report.advanced_filter(request)

#经销商数据筛选页面
@render_to('dealerfilter.html')
def dealer_filter(request):
    return dealer_report.dealer_filter(request)

#ajax返回筛选数据的表格
@render_to('dealer_result.html')
def ajax_filter(request):
    return dealer_report.ajax_filter(request)

@login_required
@render_to('dealer_list.html')
def dealer_list(request):
    return dealer_report.dealer_list(request)


#经销商单店报告页面（详细）--有paperid（管理员登录时）
@render_to('dealeranalysis.html')
def report(request, report_id):
    return dealer_report.report(request, report_id)

#经销商历史现在未来报告（详细）
@render_to('hnfreport.html')
def history_now_future_report(request, report_id):
    return dealer_report.history_now_future_report(request, report_id)

#经销商数据对比页面
@render_to('dealercompare.html')
def papers_compare(request):
    return dealer_report.papers_compare(request)

#经销商数据对比页面
@render_to('dealercompare.html')
def downloadreports(request):
    return dealer_report.downloadreports(request)

#下载单店报告
def download_report(request, dealer_id, term_id):
    return dealer_report.download_report(request, dealer_id, term_id)

#大区对比
@render_to('comparison/advancedsearch.html')
def advanced_search(request, kind):
    return dealer_report.advanced_search(request, kind)
#ajax返回筛选数据的表格
@render_to('comparison/ajax_dealer_group_result.html')
def ajax_dealer_group_result(request):
    return dealer_report.ajax_dealer_group_result(request)
#品牌对比
@render_to('comparison/advancedbrand.html')
def advanced_brand(request):
    return dealer_report.advanced_brand(request)

#ajax返回筛选数据的表格
@render_to('comparison/ajax_brand_dealer_result.html')
def ajax_brand_result(request):
    return dealer_report.ajax_brand_result(request)



#区域历史现在未来报告（详细）
@render_to('hnf_group_report.html')
def history_now_future_group_report(request, kind, report_id):
    return dealer_report.history_now_future_group_report(request, kind, report_id)

#区域数据对比页面
@render_to('comparison/dealer_group_compare.html')
def items_compare(request):
    return dealer_report.items_compare(request)

#进入访问员、进店人数、新店和老店数据对比页面
@render_to('comparison/allfilter.html')
def all_filter(request, kind):
    return dealer_report.all_filter(request, kind)

#访问员、进店人数、新店和老店---返回结果
@render_to('comparison/ajax_result.html')
def ajax_all_filter(request):
    return dealer_report.ajax_all_filter(request)

#访问员、进店人数、新店和老店数据对比
@render_to('comparison/otherreport_compare.html')
def otherreport_compare(request):
    return dealer_report.otherreport_compare(request)

@render_to('dealerlogin.html')
def dealerLogin(request):
    return dealer_report.dealerLogin(request)

def download_history_report(request, dealer_id, term_id):
    return dealer_report.download_history_report(request, dealer_id, term_id)

@csrf_exempt
@requires_csrf_token
def ajax_gen_compare_excel(request):
    return dealer_report.ajax_gen_compare_excel(request)

@csrf_exempt
@requires_csrf_token
def ajax_gen_other_compare_excel(request):
    return dealer_report.ajax_gen_other_compare_excel(request)

@csrf_exempt
@login_required
def ajax_get_option(request):
    if request.method == "POST":
        stype = request.POST.get('type', None)
        if not stype:
            return HttpResponseNotFound(u'错误请求')
        
        region_id = int(request.POST.get('region', 0))
        province_id = int(request.POST.get('province', 0))
        
        user = request.user
        up, create = UserProfile.objects.get_or_create(user=user)
        man_dealer = up.dealer
        man_dealer_list = Dealer.objects.filter(name=man_dealer.name)
        
        res = []
        if stype == 'province':
            province_list = Dealer.objects.filter(sf_parent__id=int(region_id),level=5)
            #全国
            if man_dealer and man_dealer.level == 0:
                provinces = province_list
            #大区    
            if man_dealer and man_dealer.level == 1:
                provinces = province_list.filter(sf_parent=man_dealer)
            #小区   
            if man_dealer and man_dealer.level == 4:
                provinces = province_list.filter(sf_parent=man_dealer.xq_parent)
            #经销商  
            if man_dealer and man_dealer.level == 3:
                provinces = [man_dealer.sf_parent.sf_parent]
            
            for province in provinces:
                obj = [province.id, province.name_cn]
                res.append(obj)
                
        elif stype == 'city':
            city_list = Dealer.objects.filter(sf_parent__id=int(province_id),level=2)
            #全国
            if man_dealer and man_dealer.level == 0:
                citys = city_list
            #大区    
            if man_dealer and man_dealer.level == 1:
                citys = city_list.filter(sf_parent__sf_parent=man_dealer,level=2)
            #小区   
            if man_dealer and man_dealer.level == 4:
                citys = city_list.filter(sf_parent__sf_parent=man_dealer.xq_parent,level=2)
            #经销商  
            if man_dealer and man_dealer.level == 3:
                citys = [man_dealer.parent]
            
            for city in citys:
                obj = [city.id, city.name_cn]
                res.append(obj)
                
        elif stype == 'area':
            #全国
            if man_dealer and man_dealer.level == 0:
                areas = Dealer.objects.filter(xq_parent__id=int(region_id),level=4)
            #大区    
            if man_dealer and man_dealer.level == 1:
                areas = Dealer.objects.filter(xq_parent=man_dealer,level=4)
            #小区   
            if man_dealer and man_dealer.level == 4:
                areas = [man_dealer]
            #经销商  
            if man_dealer and man_dealer.level == 3:
                areas = [man_dealer.xq_parent]
            
            for area in areas:
                obj = [area.id, area.name_cn]
                res.append(obj)
                
        elif stype == 'group':
            #全国
            if man_dealer and man_dealer.level == 0:
                dealers = Dealer.objects.filter(parent__parent__id=int(region_id),level=3)
                jt_id_list = [d.jt_parent.id for d in dealers if d.jt_parent]
                groups = Dealer.objects.filter(id__in=jt_id_list,level=6)
            #大区    
            if man_dealer and man_dealer.level == 1:
                dealers = Dealer.objects.filter(parent__parent=man_dealer,level=3)
                jt_id_list = [d.jt_parent.id for d in dealers if d.jt_parent]
                groups = Dealer.objects.filter(id__in=jt_id_list,level=6)
            #小区   
            if man_dealer and man_dealer.level == 4:
                dealers = Dealer.objects.filter(xq_parent=man_dealer,level=3)
                jt_id_list = [d.jt_parent.id for d in dealers if d.jt_parent]
                groups = Dealer.objects.filter(id__in=jt_id_list,level=6)
            #经销商  
            if man_dealer and man_dealer.level == 3:
                groups = [man_dealer.jt_parent for man_dealer in man_dealer_list if man_dealer.jt_parent]
            
            for group in groups:
                obj = [group.id, group.name_cn]
                res.append(obj)
                        
        else:
            return HttpResponseNotFound(u'错误请求')
    else:
        return HttpResponseNotFound(u'错误请求')
    
    result = simplejson.dumps(res)
    return HttpResponse(result)

url_list = pageman.patterns('DealerReport', '',
    pageman.MyUrl(None, index, name=None),
    pageman.MyUrl('dealeranalysis', dealer_analysis, name='dealeranalysis'),
    pageman.MyUrl('advancedfilter', advanced_filter, name='advancedfilter'),
    pageman.MyUrl('dealerlogin', dealerLogin, name='dealerlogin'),
    pageman.MyUrl('dealerfilter', dealer_filter, name='dealerfilter'),
    pageman.MyUrl('ajaxfilter', ajax_filter, name='ajaxfilter'),
    pageman.MyUrl('dealerlist', dealer_list, name='dealerlist'),
    pageman.MyUrl('paperscompare', papers_compare, name='paperscompare'),
    pageman.MyUrl('downloadreports', downloadreports, name='downloadreports'),
    pageman.MyUrl('ajaxgetoption', ajax_get_option, name='ajax_get_option'),
    
    pageman.MyUrl('advancedsearch/(?P<kind>\w+)/', advanced_search, name='advancedsearch'),
    pageman.MyUrl('ajaxdealergroupresult', ajax_dealer_group_result, name='ajaxdealergroupresult'),
    url(r'^DealerReport/HNFTrendReport/(?P<kind>\w+)/(?P<report_id>\d+)/$', history_now_future_group_report, name="DealerReport/HNFTrendReport"),
    pageman.MyUrl('advancedbrand', advanced_brand, name='advancedbrand'),
    pageman.MyUrl('ajaxbrandresult', ajax_brand_result, name='ajaxbrandresult'),
    pageman.MyUrl('itemscompare', items_compare, name='itemscompare'),
    pageman.MyUrl('allfilter/(?P<kind>\w+)/', all_filter, name='allfilter'),
    pageman.MyUrl('ajaxallfilter', ajax_all_filter, name='ajaxallfilter'),
    pageman.MyUrl('otherreportcompare', otherreport_compare, name='otherreportcompare'),
    url(r'^DealerReport/HNFDealerReport/(?P<report_id>\d+)/$', history_now_future_report, name="DealerReport/HNFDealerReport"),
    url(r'^DealerReport/DetailDealerReport/(?P<report_id>\d+)/$', report, name="DealerReport/DetailDealerReport"),
    url(r'^DealerReport/downloadreport/(?P<dealer_id>\d+)/(?P<term_id>\d+)/$', download_report, name="DealerReport/downloadreport"),
    pageman.MyUrl('downloadhistoryreport/(?P<dealer_id>\d+)/(?P<term_id>\d+)/$', download_history_report, name='downloadhistoryreport'),
    pageman.MyUrl('ajax_gen_compare_excel', ajax_gen_compare_excel, name='ajaxgencompareexcel'),
    pageman.MyUrl('ajax_gen_other_compare_excel', ajax_gen_other_compare_excel, name='ajaxgenothercompareexcel')
)

