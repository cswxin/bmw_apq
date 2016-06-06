# -- encoding=utf-8 --
from django.contrib import admin
from django.contrib.auth.models import User
from django.shortcuts import HttpResponseRedirect
from django.utils.encoding import force_unicode
from actions import enablereport_action, audit_action
from django.utils.translation import ugettext as _
from models import Paper, Term, ReportDocument, ReportImage, ReportSound, XslReport, Dealer, Router, PaperDiff, QuestionDiff

from django.utils.functional import update_wrapper

from django.contrib.admin.views.main import ChangeList
import enums
import mc
import os, sys
from django.conf import settings
from service.core._paper import get_paper_part_html, save_paper_part_data

from paperfilter import AREA_VAR, AreaFilterSpec, DEALER_TYPE_VAR, DealerTypeFilterSpec, TERM_VAR, TermFilterSpec
from service.core._user import has_fh_end_audit_perm, has_qc1_audit_perm
from service.core import _term

class ReportChangeList(ChangeList):
    def get_results(self, request):
        from service.core._user import has_manage_perm, has_input_perm
        
        user = request.user
        qs = self.query_set
        
        if has_manage_perm(user):
            pass
        elif has_input_perm(user):
            #录入权限只能看自己上传的图片，声音
            qs = qs.filter(user=user)
            pass
        
        self.query_set = qs
        return super(ReportChangeList, self).get_results(request)
    
class PaperChangeList(ChangeList):
    def get_results(self, request):
        from service.core._user import has_perm_define, has_tran_perm, has_input_perm, is_only_input, check_user_in_gfk_group, check_user_in_fh_group
        
        user = request.user
        paper_types = []
        if check_user_in_gfk_group(user):
            paper_types.append(enums.FW_PAPER_TYPE)
        if check_user_in_fh_group(user):
            paper_types.append(enums.FH_PAPER_TYPE)
        qs = self.query_set
        qs = qs.filter(project__id__gt=1)
        if has_perm_define(user, enums.MANAGER_PERMISSION):
            #管理员权限没有限制(能看到三种类型的问卷（GFK，FHT，BMW）)
            pass
        elif has_perm_define(user, enums.SHOW_ALL_PAPERS):
            if has_perm_define(user, enums.FW_AREA_AUDIT_PERMISSION, enums.FH_END_AUDIT_PERMISSION):
                qs = qs.filter(paper_type__in=paper_types)
        elif is_only_input(user):
            #录入权限只能看自己的
            qs = qs.filter(user=user, paper_type__in=paper_types)
            self.list_display.remove('is_public')
            self.list_display.remove('report_down')
        elif has_tran_perm(user):
            #翻译员只能看到FW团队的研究问卷（GFK）与终审问卷（BMW）
            self.list_display.remove('operate_name')
#            self.list_display.remove('image_upload')
#            self.list_display.remove('sound_upload')
            self.list_display.remove('report_down')
            qs = qs.filter(status__gte=enums.FW_PAPER_STATUS_WAIT_AUDIT_6, paper_type__in=[enums.FW_PAPER_TYPE, enums.BMW_PAPER_TYPE]).exclude(status=enums.PAPER_STATUS_FINISH, paper_type=enums.FW_PAPER_TYPE)
        else:
            #其他权限无法提交
            self.list_display.remove('operate_name')
            #self.list_display.remove('image_upload')
            #self.list_display.remove('sound_upload')
            self.list_display.remove('report_down')
            qs = qs.filter(status__gte=enums.FW_PAPER_STATUS_WAIT_AUDIT_1)
            if len(paper_types) > 0:
                qs = qs.filter(paper_type__in=paper_types)
        
        if self.areaid:
            dealer = mc.get_dealer(id=self.areaid)
            ds = mc.get_sub_node(self.areaid, 'area')
            if ds:
                qs = qs.filter(dealer__parent__in=ds).distinct()
            
        if self.dealertype:
            qs = qs.filter(dealer__dealertype=self.dealertype)
        
        if self.termid:
            qs = qs.filter(term__id=self.termid)
        
        qs = qs.filter(term=_term.get_cur_input_term())
        
        self.query_set = qs
        
        return super(PaperChangeList, self).get_results(request)

    def get_query_set(self):
        self.areaid = 0
        if AREA_VAR in self.params:
            self.areaid = int(self.params[AREA_VAR])
            del self.params[AREA_VAR]
#            if self.areaid:
#                self.params[AREA_VAR] = self.areaid
        
        self.dealertype = 0
        if DEALER_TYPE_VAR in self.params:
            self.dealertype = int(self.params[DEALER_TYPE_VAR])
            del self.params[DEALER_TYPE_VAR]
#            if self.dealertype:
#                self.params[DEALER_TYPE_VAR] = self.dealertype
        
        self.termid = 0
        if TERM_VAR in self.params:
            self.termid = int(self.params[TERM_VAR])
            del self.params[TERM_VAR]
#            if self.termid:
#                self.params[TERM_VAR] = self.termid
        
        return super(PaperChangeList, self).get_query_set()
    
class PaperAdmin(admin.ModelAdmin):
    list_display = ('term', 'survey_code', 'visitor_name', 'paper_type_code', 'dealer', 'dealer_name', 'type', 'edit_area', 'operate_name', 'status_name', 'is_public', 'report_down', 'image_file', 'image_upload', 'paper_score',)
    list_filter = ('survey_code', 'status', 'visit_begin', 'visit_end')
    search_fields = ('paper_type', 'dealer__name', 'project__name', 'survey_code', 'status')
    #ordering = ['-created']
    #list_editable = ('status',)

    actions = []

    list_per_page = 20
    
    def paper_type_code(self, obj):
        return '%s(%s)' % (dict(enums.CHOICES_PAPER_TYPE)[obj.paper_type], obj.paper_type)
    paper_type_code.short_description = u'团队'
    def paper_score(self, obj):
        if obj.score is None :
            if obj.paper_type == enums.BMW_PAPER_TYPE:
                paperdiffs = PaperDiff.objects.filter(final_paper=obj)
                if len(paperdiffs) > 0:
                    return u'<div style="background:red"><a style="color:white" href="/admin/mc/questiondiff/?paper_diff__id__exact=%d">%s</a></div>' % (paperdiffs[0].id, u'有差异')
                return u'无'
            else:
                return u'未知'
        return '%.2f' % obj.score
    paper_score.short_description = u'得分'
    paper_score.autoescape = True
    paper_score.allow_tags = True
    
    def visitor_name(self, obj):
        resp = obj.respondent
        if resp:
            user = resp.user
            if user:
                return u'%s%s' % (user.last_name, user.first_name)
        
        return ''

    visitor_name.short_description = u'评估员姓名'
    
    def dealer_name(self, obj):
        dealer = obj.dealer
        if dealer:
            return u'%s' % (dealer.name_cn or '')
        
        return ''

    dealer_name.short_description = u'全称'

    def operate_name(self, obj):
        if obj.status == enums.FW_PAPER_STATUS_INIT or obj.status == enums.FH_PAPER_STATUS_INPUT:
            name = u'<span id="submittip_%d"><a href="javascript:void(0)" class="submitpaperlink" paperid="%d">提交</a></span>' % (obj.id, obj.id)
        else:
            name = '已经提交'
        return name
    operate_name.short_description = u'提交操作'
    operate_name.autoescape = True
    operate_name.allow_tags = True
    
    def status_name(self, obj):
         return u'<span id="status_label_%d">%s</span>' % (obj.id, dict(enums.CHOICES_PAPER_STATUS)[obj.status])
    
    status_name.short_description = u'状态'
    status_name.autoescape = True
    status_name.allow_tags = True
    
    
    def bmwpaperstatus(self, obj):
        if obj.paper_type == enums.BMW_PAPER_TYPE:
            diff = PaperDiff.objects.filter(final_paper=obj);
            if len(diff) > 0:
                return dict(enums.CHOICES_DIFF_STATUS)[diff[0].status]
        return '无须审核'
    bmwpaperstatus.short_description = u'BMW问卷状态'
    bmwpaperstatus.autoescape = True
    bmwpaperstatus.allow_tags = True
             
    def type(self, obj):
        name = obj.project.name
        return name
    
    type.short_description = u'问卷类型'
    type.autoescape = True
    type.allow_tags = True

    def edit_area(self, obj):
        url = u'/admin/mc/paper/%d' % obj.id
        
        if obj.project.id > 1:
            name = u'<a href="%(items)s?p=basic">基础信息</a>  <a href="%(items)s?p=a">A部分</a> <a href="%(items)s?p=b">B部分</a> <a href="%(items)s?p=c">C部分</a> <a href="%(items)s?p=d">D部分</a> <a href="%(items)s?p=e">E部分</a> <a href="%(items)s?p=f">F部分</a> <a href="%(items)s?p=g">G部分</a>' % {'items':url}
            if obj.project.id == 4:
                name = u'<a href="%(items)s?p=basic">基础信息</a>  <a href="%(items)s?p=a">A部分</a> <a href="%(items)s?p=b">B部分</a> <a href="%(items)s?p=c">C部分</a> <a href="%(items)s?p=d">D部分</a> <a href="%(items)s?p=e">E部分</a> <a href="%(items)s?p=g">G部分</a>' % {'items':url}
        elif mc.is_q3(obj):
            name = u'<a href="%(items)s?p=basic">基础信息</a>  <a href="%(items)s?p=a">A部分</a> <a href="%(items)s?p=b">B部分</a> <a href="%(items)s?p=c">C部分</a> <a href="%(items)s?p=d">D部分</a> <a href="%(items)s?p=e">E部分</a> <a href="%(items)s?p=f">F部分</a> <a href="%(items)s?p=g">G部分</a> <a href="%(items)s?p=n">新增加部分</a> <a href="%(items)s?p=h">H部分</a>' % {'items':url}
        else:
            name = u'<a href="%(items)s?p=basic">基础信息</a>  <a href="%(items)s?p=a">A部分</a> <a href="%(items)s?p=b">B部分</a> <a href="%(items)s?p=c">C部分</a> <a href="%(items)s?p=d">D部分</a> <a href="%(items)s?p=e">E部分</a> <a href="%(items)s?p=f">F部分</a> <a href="%(items)s?p=g">G部分</a>  <a href="%(items)s?p=h">H部分</a>' % {'items':url}
        return name
    
    edit_area.short_description = u'编辑问卷'
    edit_area.autoescape = True
    edit_area.allow_tags = True
    
    def report_down(self, obj):
        name = u''
        url = u''
        try:
            xsl = XslReport.objects.get(paper=obj)
            f = xsl.xslfile
            if f:
                url = f.url
        except XslReport.DoesNotExist:
            pass
        
        name = u'<span id="downloadreport_%d">' % obj.id
        if url:
            name += u'<a href="%s">下载</a>  ' % url
        else:
            name += u' '
        name += u'</span> '
        
        if obj.status == enums.PAPER_STATUS_FINISH:
            name += u'  <a class="genreport" paperid="%d" href="javascript:void(0)">生成报告</a>' % obj.id
        else:
            name = ''
        
        return name
    
    report_down.short_description = u'单店报告'
    report_down.autoescape = True
    report_down.allow_tags = True

    def sound_file(self, obj):
        imagecount = ReportSound.objects.filter(paper=obj).count()
        name = u'<a href="/admin/mc/reportsound/?paper__id__exact=%d" target="_blank">查看(%d)</a>  ' % (obj.id, imagecount)
        return name

    sound_file.short_description = u'录音文件'
    sound_file.autoescape = True
    sound_file.allow_tags = True

    def sound_upload(self, obj):
        imagecount = ReportSound.objects.filter(paper=obj).count()
        name = u'<a href="/admin/mc/reportsound/add/?paper=%d" target="_blank">上传</a>' % obj.id
        return name
    
    sound_upload.short_description = u'录音上传'
    sound_upload.autoescape = True
    sound_upload.allow_tags = True
    
    def image_file(self, obj):
        imagecount = ReportImage.objects.filter(paper=obj).count()
        name = u'<a href="/admin/mc/reportimage/?paper__id__exact=%d" target="_blank">查看(%d)</a> ' % (obj.id, imagecount)
        return name
    
    image_file.short_description = u'图片文件'
    image_file.autoescape = True
    image_file.allow_tags = True
    
    def image_upload(self, obj):
        name = u'<a href="/admin/mc/reportimage/add/?paper=%d" target="_blank">上传</a>' % obj.id
        return name
    
    image_upload.short_description = u'图片上传'
    image_upload.autoescape = True
    image_upload.allow_tags = True
    
    #更改问卷
    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        if add:
            #添加问卷
            html = get_paper_part_html(request, 'basic', None, None)
            pass
        if change:
            #修改现有的问卷
            part = request.GET.get('p', 'basic')
            respondent = obj.respondent
            html = get_paper_part_html(request, part, respondent, obj)

        newdata = {'paperhtml':html, }
        context.update(newdata)
        next_part = self.get_next_part(request, obj)
        if next_part:
            next_part = next_part.upper()
        context.update({'next_part':next_part, })
        return super(PaperAdmin, self).render_change_form(request, context, add, change, form_url, obj)

    def get_next_part(self, request, paper):
        part = request.GET.get('p', 'basic')
        if mc.get_paper_project_id(paper) == 4:
            part_list = ['basic', 'a', 'b', 'c', 'd', 'e', 'g']
        elif mc.is_2012(paper):
            part_list = ['basic', 'a', 'b', 'c', 'd', 'e', 'f', 'g']
        elif not mc.is_q3(paper):
            part_list = ['basic', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        else:
            part_list = ['basic', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'n', 'h']
        
        index = part_list.index(part)
        if index == (len(part_list) - 1):
            next_part = None
        else:
            next_part = part_list[index + 1]
        return next_part
    
    def changelist_view(self, request, extra_context=None):
        user = request.user
        actions = []
        from service.core._user import has_qc1_audit_perm, has_qc2_audit_perm, has_qc3_audit_perm, has_manage_perm
        from service.core._user import has_dd_audit_perm, has_yj_audit_perm, has_end_audit_perm
        from service.core._user import has_fh_audit_perm, has_fh_end_audit_perm, check_user_in_gfk_group
        is_manager = has_manage_perm(user)
        if is_manager or has_qc1_audit_perm(user):
            actions.append(audit_action.qc1_audit)
        if is_manager or has_qc2_audit_perm(user):
            actions.append(audit_action.qc2_audit) 
        if is_manager or has_qc3_audit_perm(user):
            actions.append(audit_action.qc3_audit) 
        if is_manager or has_dd_audit_perm(user):
            actions.append(audit_action.dd_audit) 
        if is_manager or has_yj_audit_perm(user):
            actions.append(audit_action.yj_audit) 
        if is_manager or has_end_audit_perm(user):
            actions.append(audit_action.end_audit) 
        if is_manager or has_end_audit_perm(user) or has_dd_audit_perm(user):
            actions.append(audit_action.cancel_audit) 
            actions.append(audit_action.qc3_re_audit)
        if is_manager or has_end_audit_perm(user) or has_dd_audit_perm(user) or has_fh_end_audit_perm(user):
            #actions.append(audit_action.save_all)
            actions.append(audit_action.gen_report_bentch)
            pass
            
        if is_manager or  has_fh_audit_perm(user):
            actions.append(audit_action.fh_audit) 
        if is_manager or  has_fh_end_audit_perm(user):
            actions.append(audit_action.fh_end_audit) 
            actions.append(audit_action.fh_cancel_audit) 
        if is_manager:
            actions.append(enablereport_action.enablereport)
            actions.append(enablereport_action.disablereport)
            

#        if is_manager or has_dd_audit_perm(user) or has_yj_audit_perm(user):
#            if 'bmwpaperstatus' not in self.list_display:
#                self.list_display.append('bmwpaperstatus')
#        else:
#            if 'bmwpaperstatus'  in self.list_display:
#                self.list_display.remove('bmwpaperstatus')
                
        def __replace_desc(no, description):
            desc = description 
            splits = desc.split('.', 2)
            size = len(splits)
            if size == 2:
                desc = splits[1]
            return desc
        
#        for i, act in enumerate(actions):
#            no = '%02d' % (i + 1)
#            desc = __replace_desc(no, act.short_description)
#            act.short_description = u'%s. %s' % (no, desc)
                
        setattr(PaperAdmin, 'actions', actions) #此处要动态设置PaperAdmin类的actions属性才有效
        
        #下面for是将django 加的权限操作前加上序号，序号从actions值后算起
#        i = 0
#        for (name, func) in self.admin_site.actions:
#            description = getattr(func, 'short_description', name.replace('_', ' '))
#            vals = description._proxy____args #值为元组
#            if len(vals) > 0:
#                v = _(vals[0])
#                no = '%02d' % (i + 1 + len(actions))
#                desc = __replace_desc(no, v)
#                v2 = ('%s. %s' % (no, desc))
#                changed = []
#                changed.append(v2)
#                if len(vals) > 1:
#                    changed.extend(vals[1:])
#                description._proxy____args = tuple(changed)
#            i += 1
        if extra_context is None:
            extra_context = {}
        extra_context['has_manage_role'] = is_manager
        extra_context['is_fw_team'] = check_user_in_gfk_group(user)
        return super(PaperAdmin, self).changelist_view(request, extra_context)
         
    def response_change(self, request, obj):
        next_part = self.get_next_part(request, obj)
        
        opts = obj._meta
        pk_value = obj._get_pk_val()
        msg = _('The %(name)s "%(obj)s" was changed successfully.') % {'name': force_unicode(opts.verbose_name), 'obj': force_unicode(obj)}
        
        if request.POST.has_key("_saveandtonext"):
            self.message_user(request, msg)
            return HttpResponseRedirect("../%s/?p=%s" % (pk_value, next_part))
        else:
            return super(PaperAdmin, self).response_change(request, obj)
        
    def response_add(self, request, obj, post_url_continue='../%s/'):
        next_part = self.get_next_part(request, obj)
        
        opts = obj._meta
        pk_value = obj._get_pk_val()
        msg = _('The %(name)s "%(obj)s" was added successfully.') % {'name': force_unicode(opts.verbose_name), 'obj': force_unicode(obj)}
        
        if request.POST.has_key("_saveandtonext"):
            self.message_user(request, msg)
            return HttpResponseRedirect("../%s/?p=%s" % (pk_value, next_part))
        else:
            return super(PaperAdmin, self).response_add(request, obj, post_url_continue)
        
            
    def get_changelist(self, request, **kwargs):
        return PaperChangeList

    def save_model(self, request, obj, form, change):
        user = request.user
        from service.core._user import has_tran_perm, has_manage_perm, has_input_perm, get_user_max_perm
        from service.core._user import has_fw_input_perm, has_fh_input_perm, has_fh_audit_perm, has_perm_define
        
        max_perm = get_user_max_perm(user)
#        if not has_manage_perm(user) and not has_input_perm(user) and not has_tran_perm(user) and max_perm < obj.status:
#            return
        if not obj.id:
            pass
        elif has_tran_perm(user) :
            pass
        elif obj.is_public or obj.status == enums.PAPER_STATUS_FINISH:
            return
        elif max_perm < obj.status:
            #权限比状态大的能修改问卷
            return
        #其他人都可以修改问卷
        
        part = request.GET.get('p', 'basic')
        respondent = obj.respondent
        respondent = save_paper_part_data(request, part, respondent, obj)
        
        #获得期数，经销商
        obj.dealer = respondent.dealer
        obj.term = respondent.term
        obj.survey_code = respondent.survey_code
        obj.visit_begin = respondent.visit_begin
        obj.visit_end = respondent.visit_end
        obj.visitor_num = respondent.visitor_numb
        obj.project = respondent.project
        
        if not obj.status:
            if has_fw_input_perm(user):
                obj.status = enums.FW_PAPER_STATUS_INIT
                obj.paper_type = enums.FW_PAPER_TYPE
            elif has_fh_input_perm(user):
                obj.status = enums.FH_PAPER_STATUS_INPUT
                obj.paper_type = enums.FH_PAPER_TYPE
        
        obj.respondent = respondent
        if hasattr(obj, 'user'):
            if obj.user is None:
                obj.user = request.user
        else:
            obj.user = request.user
        obj.save()
        #统计得
        from service.core._report import calculate_paper_total_score
        calculate_paper_total_score(obj)
        obj.save()
        
        from mc import save_paper_audit_status
        if obj.status == enums.FW_PAPER_STATUS_INIT:
            #记录初始审核记录
            save_paper_audit_status(obj, request.user, enums.FW_PAPER_STATUS_INIT)
        elif obj.status == enums.FH_PAPER_STATUS_INPUT:
            #记录初始审核记录
            save_paper_audit_status(obj, request.user, enums.FH_PAPER_STATUS_INPUT)

    class Media:
        #css = {
        #    "all": ("my_styles.css",)
        #}
        js = ("/static/js/jquery-1.4.4.min.js", "/static/js/paper_admin.js",)

admin.site.register(Paper, PaperAdmin)

class TermAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'is_active_input', 'begin', 'end', 'testonly')
    list_editable = ('is_active', 'is_active_input', 'testonly')
    
    fieldsets = (
        (None, {'fields': ('name', 'begin', 'end', 'is_active', 'is_active_input', 'testonly')}),
    )
    
    def report_file(self, obj):
        url = u'2011数据大表_Q%d.xls' % obj.id
        name = '---'
        f = os.path.join(settings.MEDIA_ROOT, 'dealer_report', url)
        name = u"<a href='./genreport/%s/'>生成数据大表</a>&nbsp;&nbsp;" % obj.id
        if os.path.exists(f):
            name += u'<a href="/file/dealer_report/%s" >%s</a>' % (url, url)
        return name
    
    report_file.short_description = u'数据大表'
    report_file.autoescape = True
    report_file.allow_tags = True

    def gen_report(self, request, term_id):
        import subprocess
        from excel import gen_big_data_table
        file_path = os.path.join("mc", "excel", "gen_big_data_table.py")
        p = subprocess.Popen("python %s %s" % (file_path, term_id), cwd=settings.SITE_ROOT)
        request.user.message_set.create(message=u"生成报告中，请等待五分钟后刷新此页面...")
        return HttpResponseRedirect("../../")
        

    def get_urls(self):
        from django.conf.urls.defaults import patterns, url
        urls = super(TermAdmin, self).get_urls()
        
        def warp(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)
        
        info = self.model._meta.app_label, self.model._meta.module_name

        all_url = patterns('',
                           url(r'^genreport/(?P<term_id>\d+)/$',
                               warp(self.gen_report),
                               name='%s_%s_gen_report' % info),
            )
        return all_url + urls
    
    def paper_detail(self, obj):
        url = u'2011第%d期_问卷_信息.xls' % obj.id
        name = '---'
        f = os.path.join(settings.MEDIA_ROOT, 'dealer_report', url)
        if os.path.exists(f):
            name = u'<a href="/file/dealer_report/%s" >%s</a>' % (url, url)
        return name
    
    def save_model(self, request, obj, form, change):
        obj.save()
        from service.core._term import set_cur_input_term, set_cur_term
        if obj. is_active_input:
            set_cur_input_term(obj, refresh=True)
        if obj.is_active:
            set_cur_term(obj, refresh=True)
        
    paper_detail.short_description = u'问卷集合'
    paper_detail.autoescape = True
    paper_detail.allow_tags = True
    
admin.site.register(Term, TermAdmin)

class ReportDocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'term', 'document', 'areacode')
    
    list_filter = ('term', 'areacode')
    pass

admin.site.register(ReportDocument, ReportDocumentAdmin)

class ReportImageAdmin(admin.ModelAdmin):
    list_display = ('user', 'paper', 'image_file', 'created', 'last_modify')
    #list_filter = ('report',)
    fieldsets = (
        (None, {'fields': ('paper', 'image',)}),
    )

    def image_file(self, obj):
        name = u''
        if obj.image:
            url = obj.image.url
            name = u'<a href="%s" target="_blank">%s</a>' % (url, url)
        return name

    image_file.short_description = u'图片文件'
    image_file.autoescape = True
    image_file.allow_tags = True

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()

    def get_changelist(self, request, **kwargs):
        return ReportChangeList
    
admin.site.register(ReportImage, ReportImageAdmin)

class ReportSoundAdmin(admin.ModelAdmin):
    list_display = ('user', 'paper', 'sound_file', 'created', 'last_modify')
    fieldsets = (
        (None, {'fields': ('paper', 'sound',)}),
    )

    def sound_file(self, obj):
        name = ''
        if obj.sound:
            url = obj.sound.url
            name = u'<a href="%s" target="_blank">%s</a>' % (url, url)
        return name

    sound_file.short_description = u'声音文件'
    sound_file.autoescape = True
    sound_file.allow_tags = True

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()
        
    def get_changelist(self, request, **kwargs):
        return ReportChangeList

admin.site.register(ReportSound, ReportSoundAdmin)

#admin.site.add_action(enablereport_action.enablereport, 'enablereport')
#admin.site.add_action(enablereport_action.disablereport, 'disablereport')

#admin.site.add_action(audit_action.cancel_audit, 'cancel_audit')
#admin.site.add_action(audit_action.end_audit, 'end_audit')
#admin.site.add_action(audit_action.qc1_audit, 'qc1_audit')
#admin.site.add_action(audit_action.qc2_audit, 'qc2_audit')
#admin.site.add_action(audit_action.qc3_audit, 'qc3_audit')

class DealerAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_cn', 'city_cn', 'abbr_cn', 'province_cn')
    fieldsets = (
        (None, {'fields': ('name', 'name_cn', 'name_en', 'dealertype', 'city_cn', 'city_en', 'province_cn', 'province_en', 'address', 'abbr_cn', 'abbr_en', 'tel', 'parent')}),
    )
    
    list_filter = ('parent',)
    
    def report_down(self, obj):
        name = u''
        
        xsls = XslReport.objects.filter(dealer=obj)
        for xsl in xsls:
            name = u'<span id="downloadreport_%d">' % obj.id
            url = xsl.xslfile.url
            if url:
                name += u'<a href="%s">下载第%d期 </a>  ' % (url, xsl.term_id)
            else:
                name += u' '
            name += u'</span> '
        return name
    
    report_down.short_description = u'单店报告'
    report_down.autoescape = True
    report_down.allow_tags = True    
    
admin.site.register(Dealer, DealerAdmin)

class RouterAdmin(admin.ModelAdmin):
    list_display = ('name', 'term', 'citys', 'user')
    fieldsets = (
        (None, {'fields': ('name', 'term', 'citys', 'user')}),
    )
    
    list_filter = ('term',)
    
admin.site.register(Router, RouterAdmin)

class PaperDiffChangeList(ChangeList):
    def get_results(self, request):
        
        user = request.user
        qs = self.query_set.filter(fw_paper__term=_term.get_cur_input_term())
        self.query_set = qs
        return super(PaperDiffChangeList, self).get_results(request)
    
class PaperDiffAdmin(admin.ModelAdmin):
    list_display = ('term_name', 'dealer_name', 'fw_paper_info', 'fh_paper_info', 'bmw_paper_info', 'status_name')
    ordering = ('-status',)
    def __init__(self, *args, **kwargs):
        super(PaperDiffAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = (None,)

    def term_name(self, obj):
        return obj.fw_paper.term.name
    term_name.short_description = u'期数'
    def dealer_name(self, obj):
        return u'%s(%s)' % (obj.fw_paper.dealer.name_cn, obj.fw_paper.dealer.name)
    dealer_name.short_description = u'经销商'
    def fw_paper_info(self, obj):
        paper = obj.fw_paper
        return u'%s%s-%d' % (paper.user.username, paper.user.first_name, paper.id)
    fw_paper_info.short_description = u'FWT信息'
    def fh_paper_info(self, obj):
        paper = obj.fh_paper
        return u'%s%s-%d' % (paper.user.username, paper.user.first_name, paper.id)
    fh_paper_info.short_description = u'FHT信息'
    def bmw_paper_info(self, obj):
        paper = obj.final_paper
        ret = ''
        if paper:
            ret = u'%s%s-%d' % (paper.user.username, paper.user.first_name, paper.id)
        return ret
    bmw_paper_info.short_description = u'BMW信息'
    
    def status_name(self, obj):
        st_name = dict(enums.CHOICES_DIFF_STATUS)[obj.status]
        if obj.status == enums. HAS_CONFLICT:
            return u'<div style="background:red"><a style="color:white" href="/admin/mc/questiondiff/?paper_diff__id__exact=%d">%s</a></div>' % (obj.id, st_name)
        elif obj.status == enums.FIXED_CONFLICT:
            return u'%s- %s' % (st_name, obj.bmw.username)
        else: 
            return st_name
    status_name.short_description = u'状态'
    status_name.autoescape = True
    status_name.allow_tags = True
    
    def get_changelist(self, request, **kwargs):
        return PaperDiffChangeList
    
admin.site.register(PaperDiff, PaperDiffAdmin)

class QuestionDiffChangeList(ChangeList):
    def get_results(self, request):
        qs = self.query_set.filter(paper_diff__fw_paper__term=_term.get_cur_input_term())
        self.query_set = qs
        return super(QuestionDiffChangeList, self).get_results(request)
    
class QuestionDiffAdmin(admin.ModelAdmin):
    list_display = ('term_name', 'dealer_name', 'fw_paper_info', 'fh_paper_info', 'bmw_paper_info', 'question', 'fw_q_score', 'fw_q_comment_d', 'fh_q_score', 'fh_q_comment_d', 'final_q_score', 'final_q_comment_d')
#    fieldsets = (
#        (None, {'fields': ('name', 'term', 'citys', 'user')}),
#    )
    def __init__(self, *args, **kwargs):
        super(QuestionDiffAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = (None,)
    def term_name(self, obj):
        return obj.paper_diff.fw_paper.term.name
    term_name.short_description = u'期数'
    def dealer_name(self, obj):
        return u'%s(%s)' % (obj.paper_diff.fw_paper.dealer.name_cn, obj.paper_diff.fw_paper.dealer.name)
    dealer_name.short_description = u'经销商'
    def fw_paper_info(self, obj):
        paper = obj.paper_diff.fw_paper
        return u'%s%s-%d' % (paper.user.username, paper.user.first_name, paper.id)
    fw_paper_info.short_description = u'FWT信息'
    
    def fh_paper_info(self, obj):
        paper = obj.paper_diff.fh_paper
        return u'%s%s-%d' % (paper.user.username, paper.user.first_name, paper.id)
    fh_paper_info.short_description = u'FHT信息'
    
    def bmw_paper_info(self, obj):
        paper = obj.paper_diff.final_paper
        ret = ''
        if paper:
            ret = u'%s%s-%d' % (paper.user.username, paper.user.first_name, paper.id)
        return ret
    bmw_paper_info.short_description = u'BMW信息'
    
    def fw_q_comment_d(self, obj):
        return obj.fw_q_comment;
    def fh_q_comment_d(self, obj):
        return obj.fh_q_comment;
    def final_q_comment_d(self, obj):
        return obj.final_q_comment;
    fw_q_comment_d.autoescape = True
    fw_q_comment_d.allow_tags = True
    fh_q_comment_d.autoescape = True
    fh_q_comment_d.allow_tags = True
    final_q_comment_d.autoescape = True
    final_q_comment_d.allow_tags = True
    
    def get_changelist(self, request, **kwargs):
        return QuestionDiffChangeList
    
admin.site.register(QuestionDiff, QuestionDiffAdmin)
