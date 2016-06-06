#encoding:utf-8

from django.shortcuts import HttpResponseRedirect
from django.core.urlresolvers import reverse
from mcview.decorator import render_to
from service import project_status 
from mcview import pageman
from django.conf.urls.defaults import url
from django.views.decorators.csrf import csrf_exempt

@render_to('index.html')
def index(request):
    return locals()

@render_to('national.html')
def national(request):
    return project_status.overview(request)

@render_to('reginal.html')
def reginal(request):
    return project_status.reginal(request)

@render_to('dealer.html')
def dealer(request):
    return project_status.dealer(request)

@render_to('mini.html')
def mini(request):
    return project_status.mini(request)

@render_to('others.html')
def others(request):
    return project_status.others(request)

@render_to('route.html')    
def route(request):
    return project_status.route(request)

@csrf_exempt
@render_to('routeDiv.html')
def ajax_route(request):
    return project_status.route(request)
    
@csrf_exempt
@render_to('route.html')
def ajax_db_route(request):
    return project_status.ajax_db_route(request)

@render_to('paperconflict.html')
def paper_conflict(request):
    return project_status.paper_conflict(request)       
               
@render_to('paper_conflict_result.html')
def ajax_paper_conflict(request):
    return project_status.ajax_paper_conflict(request)

@render_to('paper_conflict_details.html')
def paper_conflict_detail(request, paperdiff_id):
    return project_status.paper_conflict_detail(request, paperdiff_id) 

@csrf_exempt
def ajax_bmw_update_question(request):
    return project_status.ajax_bmw_update_question(request) 
url_list = pageman.patterns('ProjectStatus', '',
    pageman.MyUrl(None, index, name=None),
    #url(r'^ProjectStatus/$', index,name="ProjectStatus"),
    pageman.MyUrl('national', national, name='national'),
    #url(r'^ProjectStatus/$', index,name="ProjectStatus"),
    pageman.MyUrl('reginal', reginal, name='reginal'),
    pageman.MyUrl('dealer', dealer, name='dealer'),
    pageman.MyUrl('mini', mini, name='mini'),
    pageman.MyUrl('others', others, name='others'),
    pageman.MyUrl('ajaxdbroute', ajax_db_route, name='ajaxdbroute'),
    pageman.MyUrl('route', route, name='route'),
    pageman.MyUrl('ajaxroute', ajax_route, name='ajaxroute'),
    pageman.MyUrl('paperconflict', paper_conflict, name='paperconflict'),
    pageman.MyUrl('ajaxpaperconflict', ajax_paper_conflict, name='ajaxpaperconflict'),
    pageman.MyUrl('paperconflictdetail/(?P<paperdiff_id>\d+)/', paper_conflict_detail, name='paperconflictdetail'),
    pageman.MyUrl('ajaxbmwupdatequestion', ajax_bmw_update_question, name='ajaxbmwupdatequestion'),
)
