#encoding:utf-8
from django.shortcuts import HttpResponseRedirect, Http404, HttpResponse
from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User
from django.utils import simplejson
from django.views.decorators.csrf import csrf_exempt
from service.core import _user, _report, _term
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.exceptions import PermissionDenied
import settings
import shutil
import os

@login_required
def functionlist(request):
    user = request.user
    if not _user.has_manage_perm(user):
        raise PermissionDenied
    template_file = "functionlist.html"
    cur_term = _term.get_cur_input_term()
    terms_2012 = _term.get_2012_all_terms()
    return render_to_response(template_file, locals(), context_instance=RequestContext(request))

@csrf_exempt
def trans_export_need(request):
    user = request.user
    if not _user.has_manage_perm(user):
        raise PermissionDenied
    cur_term = _term.get_cur_input_term()
    from tools.first import export
    xls_file = export.write_data(cur_term, False)
    import datetime
    time = datetime.datetime.now().strftime('%y%m%d%H%M%S')
    firstname = os.path.join(settings.MEDIA_ROOT,u'%s_tran_need_%s.xls'%(cur_term.name_cn,time))
    shutil.copyfile(xls_file, firstname)
    downloadname = os.path.basename(firstname)
    return HttpResponseRedirect('/file/%s' % (downloadname))

@csrf_exempt
def trans_export_all(request):
    user = request.user
    if not _user.has_manage_perm(user):
        raise PermissionDenied
    
    cur_term = _term.get_cur_input_term()
    from tools.first import export
    xls_file = export.write_data(cur_term, True)
    import datetime
    time = datetime.datetime.now().strftime('%y%m%d%H%M%S')
    firstname = os.path.join(settings.MEDIA_ROOT,u'%s_tran_all_%s.xls'%(cur_term.name_cn,time))
    shutil.copyfile(xls_file, firstname)
    downloadname = os.path.basename(firstname)
    return HttpResponseRedirect('/file/%s' % (downloadname))

@csrf_exempt
def trans_import(request):    
    user = request.user
    if not _user.has_manage_perm(user):
        raise PermissionDenied
    
    f = request.FILES.get("file", None)
    #存储文件
    if f:
        fpath = os.path.join(settings.MEDIA_ROOT, 'transup')
        if not os.path.exists(fpath):
            os.makedirs(fpath)
        import random
        ranid = random.randint(1, 9999)
        import datetime
        time = datetime.datetime.now().strftime('%y%m%d%H%M%S')
        filename = u'%s_trans_%s_%d.xls' % (user.username,time, ranid)
        fpath = os.path.join(fpath, filename)
        
        of = open(fpath, 'wb+')
        for chunk in f.chunks():
            of.write(chunk)
        of.close()
        shutil.copy(fpath, settings.RESOURCES_ROOT)
        
        #读取文件输出
#        try:
        cur_term = _term.get_cur_input_term()
        from tools.first import export
        export.save_tran(cur_term, filename)
#        except:
#            label = u"请上传合法的xls文件"
#            return render_to_response("functionlist.html", locals(), context_instance=RequestContext(request))
        #end
        label = u"上传成功"
    else:
        label = u"上传失败"
    terms_2012 = _term.get_2012_all_terms()
    return render_to_response("functionlist.html", locals(), context_instance=RequestContext(request))

@csrf_exempt    
def orignial_export(request, term_id):
    user = request.user
    if not _user.has_manage_perm(user):
        raise PermissionDenied
    cur_term = _term.get_term_by_id(term_id)
    from tools.first import gen_option_data
    xls_file = gen_option_data.make_excel(cur_term.id)
    shutil.copy(xls_file, settings.MEDIA_ROOT)
    downloadname = os.path.basename(xls_file)
    return HttpResponseRedirect('/file/%s' % (downloadname))

@csrf_exempt    
def score_export(request, term_id):
    user = request.user
    if not _user.has_manage_perm(user):
        raise PermissionDenied
    cur_term = _term.get_term_by_id(term_id)
    from tools.first import gen_big_data
    templateName = u'big_data/%s数据大表_template.xls'%cur_term.name_cn
    xls_file = gen_big_data.write_data(cur_term, templateName)
    shutil.copy(xls_file, settings.MEDIA_ROOT)
    downloadname = os.path.basename(xls_file)
    return HttpResponseRedirect('/file/%s' % (downloadname))

@csrf_exempt
@login_required
def submit_paper_req(request):
    from mc import get_paper_by_id, submit_paper, enums
    paperid = int(request.POST.get('paperid', 0))
    paper = get_paper_by_id(paperid)
    ret = False
    if paper:
        #TODO:权限判断 
        user = request.user
        ret = submit_paper(paper, user)
    
    sdicts = {}
    sdicts['result'] = ret and 1 or 0
    sdicts['status'] = dict(enums.CHOICES_PAPER_STATUS)[paper.status] 
    return HttpResponse(simplejson.dumps(sdicts, ensure_ascii=False))

@csrf_exempt
@login_required
def gen_report_req(request):
    from mc import get_paper_by_id, gen_report
    paperid = int(request.POST.get('paperid', 0))
    paper = get_paper_by_id(paperid)
    ret = False
    if paper:
        #TODO:权限判断 
        user = request.user
        ret = gen_report(paper, user)
        import urllib
        ret = urllib.quote(ret.encode('utf-8'))
    
    sdicts = {}
    sdicts['result'] = ret and 1 or 0
    sdicts['purl'] = ret
    return HttpResponse(simplejson.dumps(sdicts, ensure_ascii=False))

@csrf_exempt
@login_required
def aggregate_report(request):
    if _user.has_manage_perm(request.user):
        _report.aggregate_report()
        _report.aggregate_otherreport()
    sdicts = {'result':1}
    return HttpResponse(simplejson.dumps(sdicts, ensure_ascii=False))
