#!/usr/bin/python
# coding=utf-8

from django import template
from django.core.exceptions import PermissionDenied, ValidationError
from django.contrib.admin import helpers
from django.contrib.admin.util import get_deleted_objects, model_ngettext
from django.shortcuts import render_to_response
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext as _
from django.contrib import messages
from service import paperdiff
from mc.models import Report, PaperAudit
from mc import enums

from service.core._user import has_qc1_audit_perm, has_qc2_audit_perm, has_qc3_audit_perm, has_manage_perm
from service.core._user import has_dd_audit_perm, has_yj_audit_perm, has_end_audit_perm
from service.core._user import has_fh_audit_perm, has_fh_end_audit_perm

msg_paper_not_belong_gfk = u'复核团队问卷/BMW终审问卷，GFK审核流程不能操作。'
msg_paper_not_belong_fht = u'GFK团队问卷/BMW终审问卷，复核团队审核流程不能操作。'

########################################
# GFK 退回QC3重审
def qc3_re_audit(modeladmin, request, queryset):
    """
    """
    opts = modeladmin.model._meta
    app_label = opts.app_label
    
    # Populate modifiable_objects, a data structure of all related objects that will also be deleted.
    modifiable_objects, perms_needed = get_deleted_objects(queryset, opts, request.user, modeladmin.admin_site, levels_to_root=2)

    # The user has already confirmed the deletion.
    # Do the deletion and return a None to display the change list view again.  
    can_audit = validate_false_paper_have_type(queryset, [enums.FH_PAPER_TYPE, enums.BMW_PAPER_TYPE])
    if can_audit == False:
        messages.error(request, msg_paper_not_belong_gfk)
        return None
    ##督导或研究审核都是可以退回QC3重审，其他则不能
    paper_st_right = validate_false_paper_status(request, queryset, [enums.FW_PAPER_STATUS_WAIT_AUDIT_5, enums.FW_PAPER_STATUS_WAIT_AUDIT_6], u'退回QC三重审')
    if paper_st_right == False:
        return None
    if request.POST.get('post'):
        user = request.user
        # 权限判定
        #督导，终审，管理员可用
        if not has_end_audit_perm(user) and not has_manage_perm(user) and not has_dd_audit_perm(user):
            raise PermissionDenied
        
        n = queryset.count()
        if n:
            for obj in queryset :
                obj_display = force_unicode(obj)
                #remove paper FW audit info
                audits = PaperAudit.objects.filter(paper=obj, new_status__gt=enums.FW_PAPER_STATUS_WAIT_AUDIT_3)
                for au in audits:
                    au.delete()
                obj.status = enums.FW_PAPER_STATUS_WAIT_AUDIT_3
                obj.save()
                # change
                modeladmin.log_change(request, obj, obj_display)

            modeladmin.message_user(request, u'成功  退回%(count)d %(items)s 到QC三审重审.' % {
                "count": n, "items": model_ngettext(modeladmin.opts, n)
            })
        
        # Return None to display the change list page again.
        return None
    
    context = {
        "title": _("Are you sure?"),
        "object_name": force_unicode(opts.verbose_name),
        "modifiable_objects": modifiable_objects,
        'queryset': queryset,
        
        "opts": opts,
        "root_path": modeladmin.admin_site.root_path,
        "app_label": app_label,
        'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
    }
    
    # Display the confirmation page
    return render_to_response('qc3_re_audit_confirmation.html', context, context_instance=template.RequestContext(request))

########################################
# GFK取消终审
def cancel_audit(modeladmin, request, queryset):
    """
    """
    opts = modeladmin.model._meta
    app_label = opts.app_label
    
    # Populate modifiable_objects, a data structure of all related objects that will also be deleted.
    modifiable_objects, perms_needed = get_deleted_objects(queryset, opts, request.user, modeladmin.admin_site, levels_to_root=2)

    # The user has already confirmed the deletion.
    # Do the deletion and return a None to display the change list view again.  
    can_audit = validate_false_paper_have_type(queryset, [enums.FH_PAPER_TYPE, enums.BMW_PAPER_TYPE])
    if can_audit == False:
        messages.error(request, msg_paper_not_belong_gfk)
        return None
    paper_st_right = validate_false_paper_status(request, queryset, [enums.PAPER_STATUS_FINISH], u'取消终审')
    if paper_st_right == False:
        return None
    if request.POST.get('post'):
        user = request.user
        # 权限判定
        #督导，终审，管理员可用
        if not has_end_audit_perm(user) and not has_manage_perm(user) and not has_dd_audit_perm(user):
            raise PermissionDenied
        
        n = queryset.count()
        if n:
            for obj in queryset :
                obj_display = force_unicode(obj)
                #remove paper FW audit info
                audits = PaperAudit.objects.filter(paper=obj, new_status=obj.status)
                for au in audits:
                    au.delete()
                obj.status = enums.FW_PAPER_STATUS_WAIT_AUDIT_6
                obj.save()
                
               
                # change
                modeladmin.log_change(request, obj, obj_display)

            modeladmin.message_user(request, u'成功 取消 %(count)d %(items)s 终审.' % {
                "count": n, "items": model_ngettext(modeladmin.opts, n)
            })
        
        # Return None to display the change list page again.
        return None
    
    context = {
        "title": _("Are you sure?"),
        "object_name": force_unicode(opts.verbose_name),
        "modifiable_objects": modifiable_objects,
        'queryset': queryset,
        
        "opts": opts,
        "root_path": modeladmin.admin_site.root_path,
        "app_label": app_label,
        'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
    }
    
    # Display the confirmation page
    return render_to_response('cancel_audit_confirmation.html', context, context_instance=template.RequestContext(request))

def validate_false_paper_have_type(queryset, types):
    for obj in queryset :
        if obj.paper_type in types:
            return False
    return True


def validate_false_paper_status(request, queryset, paper_pre_status_list, audit_info):
    '''检查问卷是否在审核前1个状态 '''
    paper_st_right = True
    for obj in queryset :
        if obj.status not in paper_pre_status_list:
            paper_st_right = False
            messages.error(request, u'因问卷审核流程限制，%s无法操作问卷：%s' % (audit_info, obj.survey_code))
    return paper_st_right
########################################
# GFK终审确认
def end_audit(modeladmin, request, queryset):
    """
    """
    opts = modeladmin.model._meta
    app_label = opts.app_label
    
    # Populate modifiable_objects, a data structure of all related objects that will also be deleted.
    modifiable_objects, perms_needed = get_deleted_objects(queryset, opts, request.user, modeladmin.admin_site, levels_to_root=2)

    # The user has already confirmed the deletion.
    # Do the deletion and return a None to display the change list view again.    
    can_audit = validate_false_paper_have_type(queryset, [enums.FH_PAPER_TYPE, enums.BMW_PAPER_TYPE])
    if can_audit == False:
        messages.error(request, msg_paper_not_belong_gfk)
        return None
    paper_st_right = validate_false_paper_status(request, queryset, [enums.FW_PAPER_STATUS_WAIT_AUDIT_6], u'终审')
    if paper_st_right == False:
        return None
    if request.POST.get('post'):
        user = request.user
        # 权限判定
        if not has_end_audit_perm(user) and not has_manage_perm(user):
            raise PermissionDenied
        
        n = queryset.count()
        passed_papers = []
        if n:
            perm = enums.PAPER_STATUS_FINISH
            for obj in queryset :
                obj_display = force_unicode(obj)
                if obj.status < perm:
                    from mc import save_paper_audit_status
                    save_paper_audit_status(obj, request.user, perm)
                    
                    obj.status = perm
                    obj.save()
                    passed_papers.append(obj)
                    # change
                    modeladmin.log_change(request, obj, obj_display)
                else:
                    n -= 1
            modeladmin.message_user(request, u'终审通过 %(count)d %(items)s 报告.' % {
                "count": n, "items": model_ngettext(modeladmin.opts, n)
            })
            
            if len(passed_papers) > 0:
                from service.core._report import generate_report_by_paper
                generate_report_by_paper(queryset)
                conflicts_msg = []
                for paper in queryset:
                    no_conflict, diff = paperdiff.do_dealer_paper_diff(paper, user)
#                    if not no_conflict:
#                        conflicts_msg.append(u'%s(FW团队问卷: %s 与 复核团队问卷: %s 比较，产生BMW审核问卷: %s)' % (paper.dealer.name, diff.fw_paper.survey_code, diff.fh_paper.survey_code, diff.final_paper.survey_code))
#                if len(conflicts_msg) > 0:
#                    modeladmin.message_user(request, u'产生问卷差异的经销商及相关问卷信息如下:')
#                    for tmpmsg in conflicts_msg:
#                        modeladmin.message_user(request, tmpmsg)
#                else:
#                    modeladmin.message_user(request, u'并未产生问卷差异.')
        
        # Return None to display the change list page again.
        return None
    
    context = {
        "title": _("Are you sure?"),
        "object_name": force_unicode(opts.verbose_name),
        "modifiable_objects": modifiable_objects,
        'queryset': queryset,
        
        "opts": opts,
        "root_path": modeladmin.admin_site.root_path,
        "app_label": app_label,
        'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
    }
    
    # Display the confirmation page
    return render_to_response('finish_audit_confirmation.html', context, context_instance=template.RequestContext(request))

########################################
# QC1初审
def qc1_audit(modeladmin, request, queryset):
    """
    """
    opts = modeladmin.model._meta
    app_label = opts.app_label
    
    # Populate modifiable_objects, a data structure of all related objects that will also be deleted.
    modifiable_objects, perms_needed = get_deleted_objects(queryset, opts, request.user, modeladmin.admin_site, levels_to_root=2)

    can_audit = validate_false_paper_have_type(queryset, [enums.FH_PAPER_TYPE, enums.BMW_PAPER_TYPE])
    if can_audit == False:
        messages.error(request, msg_paper_not_belong_gfk)
        return None
    paper_st_right = validate_false_paper_status(request, queryset, [enums.FW_PAPER_STATUS_WAIT_AUDIT_1], u'QC一审')
    if paper_st_right == False:
        return None
        
    # The user has already confirmed the deletion.
    # Do the deletion and return a None to display the change list view again.    
    if request.POST.get('post'):
        user = request.user
        # 权限判定
        if not has_qc1_audit_perm(user) and not has_manage_perm(user):
            raise PermissionDenied
        
        n = queryset.count()
        if n:
            for obj in queryset :
                obj_display = force_unicode(obj)
                if obj.status < enums.FW_PAPER_STATUS_WAIT_AUDIT_2:
                    from mc import save_paper_audit_status
                    save_paper_audit_status(obj, request.user, enums.FW_PAPER_STATUS_WAIT_AUDIT_2)
                    
                    obj.status = enums.FW_PAPER_STATUS_WAIT_AUDIT_2
                    obj.save()
                    
                    # change
                    modeladmin.log_change(request, obj, obj_display)
                else:
                    n -= 1
                    
            modeladmin.message_user(request, u'QC一审通过 %(count)d %(items)s 报告.' % {
                "count": n, "items": model_ngettext(modeladmin.opts, n)
            })
        
        # Return None to display the change list page again.
        return None
    
    context = {
        "title": _("Are you sure?"),
        "object_name": force_unicode(opts.verbose_name),
        "modifiable_objects": modifiable_objects,
        'queryset': queryset,
        
        "opts": opts,
        "root_path": modeladmin.admin_site.root_path,
        "app_label": app_label,
        'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
    }
    
    # Display the confirmation page
    return render_to_response('qc1_audit_confirmation.html', context, context_instance=template.RequestContext(request))

########################################
# QC2审核
def qc2_audit(modeladmin, request, queryset):
    """
    """
    opts = modeladmin.model._meta
    app_label = opts.app_label
    
    # Populate modifiable_objects, a data structure of all related objects that will also be deleted.
    modifiable_objects, perms_needed = get_deleted_objects(queryset, opts, request.user, modeladmin.admin_site, levels_to_root=2)

    can_audit = validate_false_paper_have_type(queryset, [enums.FH_PAPER_TYPE, enums.BMW_PAPER_TYPE])
    if can_audit == False:
        messages.error(request, msg_paper_not_belong_gfk)
        return None
    paper_st_right = validate_false_paper_status(request, queryset, [enums.FW_PAPER_STATUS_WAIT_AUDIT_2], u'QC二审')
    if paper_st_right == False:
        return None
    # The user has already confirmed the deletion.
    # Do the deletion and return a None to display the change list view again.    
    if request.POST.get('post'):
        user = request.user
        # 权限判定
        if not has_qc2_audit_perm(user) and not has_manage_perm(user):
            raise PermissionDenied
        
        n = queryset.count()
        if n:
            for obj in queryset :
                obj_display = force_unicode(obj)
                if obj.status < enums.FW_PAPER_STATUS_WAIT_AUDIT_3:
                    from mc import save_paper_audit_status
                    save_paper_audit_status(obj, request.user, enums.FW_PAPER_STATUS_WAIT_AUDIT_3)
                    
                    obj.status = enums.FW_PAPER_STATUS_WAIT_AUDIT_3                
                    obj.save()
                    
                    # change
                    modeladmin.log_change(request, obj, obj_display)
                else:
                    n -= 1

            modeladmin.message_user(request, u'QC二审核通过 %(count)d %(items)s 报告.' % {
                "count": n, "items": model_ngettext(modeladmin.opts, n)
            })
        
        # Return None to display the change list page again.
        return None
    
    context = {
        "title": _("Are you sure?"),
        "object_name": force_unicode(opts.verbose_name),
        "modifiable_objects": modifiable_objects,
        'queryset': queryset,
        
        "opts": opts,
        "root_path": modeladmin.admin_site.root_path,
        "app_label": app_label,
        'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
    }
    
    # Display the confirmation page
    return render_to_response('qc2_audit_confirmation.html', context, context_instance=template.RequestContext(request))

########################################
# QC3审核
def qc3_audit(modeladmin, request, queryset):
    """
    """
    opts = modeladmin.model._meta
    app_label = opts.app_label
    
    # Populate modifiable_objects, a data structure of all related objects that will also be deleted.
    modifiable_objects, perms_needed = get_deleted_objects(queryset, opts, request.user, modeladmin.admin_site, levels_to_root=2)

    can_audit = validate_false_paper_have_type(queryset, [enums.FH_PAPER_TYPE, enums.BMW_PAPER_TYPE])
    if can_audit == False:
        messages.error(request, msg_paper_not_belong_gfk)
        return None
    paper_st_right = validate_false_paper_status(request, queryset, [enums.FW_PAPER_STATUS_WAIT_AUDIT_3], u'QC三审')
    if paper_st_right == False:
        return None
    # The user has already confirmed the deletion.
    # Do the deletion and return a None to display the change list view again.    
    if request.POST.get('post'):
        user = request.user
        # 权限判定
        if not has_qc3_audit_perm(user) and not has_manage_perm(user):
            raise PermissionDenied
        
        n = queryset.count()
        if n:
            for obj in queryset :
                obj_display = force_unicode(obj)
                if obj.status < enums.FW_PAPER_STATUS_WAIT_AUDIT_4:
                    from mc import save_paper_audit_status
                    save_paper_audit_status(obj, request.user, enums.FW_PAPER_STATUS_WAIT_AUDIT_4)
                    
                    obj.status = enums.FW_PAPER_STATUS_WAIT_AUDIT_4
                    obj.save()
                    
                    # change
                    modeladmin.log_change(request, obj, obj_display)
                else:
                    n -= 1

            modeladmin.message_user(request, u'QC三审核通过 %(count)d %(items)s 报告.' % {
                "count": n, "items": model_ngettext(modeladmin.opts, n)
            })
        
        # Return None to display the change list page again.
        return None
    
    context = {
        "title": _("Are you sure?"),
        "object_name": force_unicode(opts.verbose_name),
        "modifiable_objects": modifiable_objects,
        'queryset': queryset,
        
        "opts": opts,
        "root_path": modeladmin.admin_site.root_path,
        "app_label": app_label,
        'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
    }
    
    # Display the confirmation page
    return render_to_response('qc3_audit_confirmation.html', context, context_instance=template.RequestContext(request))

########################################
# 督导审核
def dd_audit(modeladmin, request, queryset):
    """
    """
    opts = modeladmin.model._meta
    app_label = opts.app_label
    
    # Populate modifiable_objects, a data structure of all related objects that will also be deleted.
    modifiable_objects, perms_needed = get_deleted_objects(queryset, opts, request.user, modeladmin.admin_site, levels_to_root=2)

    can_audit = validate_false_paper_have_type(queryset, [enums.FH_PAPER_TYPE, enums.BMW_PAPER_TYPE])
    if can_audit == False:
        messages.error(request, msg_paper_not_belong_gfk)
        return None
    paper_st_right = validate_false_paper_status(request, queryset, [enums.FW_PAPER_STATUS_WAIT_AUDIT_4], u'督导审核')
    if paper_st_right == False:
        return None
    # The user has already confirmed the deletion.
    # Do the deletion and return a None to display the change list view again.    
    if request.POST.get('post'):
        user = request.user
        # 权限判定
        if not has_dd_audit_perm(user) and not has_manage_perm(user):
            raise PermissionDenied
        
        n = queryset.count()
        if n:
            for obj in queryset :
                obj_display = force_unicode(obj)
                if obj.status < enums.FW_PAPER_STATUS_WAIT_AUDIT_5:
                    from mc import save_paper_audit_status
                    save_paper_audit_status(obj, request.user, enums.FW_PAPER_STATUS_WAIT_AUDIT_5)
                    
                    obj.status = enums.FW_PAPER_STATUS_WAIT_AUDIT_5
                    obj.save()
                    
                    # change
                    modeladmin.log_change(request, obj, obj_display)
                else:
                    n -= 1

            modeladmin.message_user(request, u'督导审核通过 %(count)d %(items)s 报告.' % {
                "count": n, "items": model_ngettext(modeladmin.opts, n)
            })
        
        # Return None to display the change list page again.
        return None
    
    context = {
        "title": _("Are you sure?"),
        "object_name": force_unicode(opts.verbose_name),
        "modifiable_objects": modifiable_objects,
        'queryset': queryset,
        
        "opts": opts,
        "root_path": modeladmin.admin_site.root_path,
        "app_label": app_label,
        'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
    }
    
    # Display the confirmation page
    return render_to_response('dd_audit_confirmation.html', context, context_instance=template.RequestContext(request))

########################################
# 研究审核
def yj_audit(modeladmin, request, queryset):
    """
    """
    opts = modeladmin.model._meta
    app_label = opts.app_label
    
    # Populate modifiable_objects, a data structure of all related objects that will also be deleted.
    modifiable_objects, perms_needed = get_deleted_objects(queryset, opts, request.user, modeladmin.admin_site, levels_to_root=2)

    
    can_audit = validate_false_paper_have_type(queryset, [enums.FH_PAPER_TYPE, enums.BMW_PAPER_TYPE])
    if can_audit == False:
        messages.error(request, msg_paper_not_belong_gfk)
        return None
    paper_st_right = validate_false_paper_status(request, queryset, [enums.FW_PAPER_STATUS_WAIT_AUDIT_5], u'研究审核')
    if paper_st_right == False:
        return None
    # The user has already confirmed the deletion.
    # Do the deletion and return a None to display the change list view again.    
    if request.POST.get('post'):
        user = request.user
        # 权限判定
        if not has_yj_audit_perm(user) and not has_manage_perm(user):
            raise PermissionDenied
        
        n = queryset.count()
        if n:
            for obj in queryset :
                obj_display = force_unicode(obj)
                if obj.status < enums.FW_PAPER_STATUS_WAIT_AUDIT_6:
                    from mc import save_paper_audit_status
                    save_paper_audit_status(obj, request.user, enums.FW_PAPER_STATUS_WAIT_AUDIT_6)
                    
                    obj.status = enums.FW_PAPER_STATUS_WAIT_AUDIT_6
                    obj.save()
                    
                    # change
                    modeladmin.log_change(request, obj, obj_display)
                else:
                    n -= 1

            modeladmin.message_user(request, u'研究审核通过 %(count)d %(items)s 报告.' % {
                "count": n, "items": model_ngettext(modeladmin.opts, n)
            })
        
        # Return None to display the change list page again.
        return None
    
    context = {
        "title": _("Are you sure?"),
        "object_name": force_unicode(opts.verbose_name),
        "modifiable_objects": modifiable_objects,
        'queryset': queryset,
        
        "opts": opts,
        "root_path": modeladmin.admin_site.root_path,
        "app_label": app_label,
        'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
    }
    
    # Display the confirmation page
    return render_to_response('yj_audit_confirmation.html', context, context_instance=template.RequestContext(request))

########################################
# 独立复核审核
def fh_audit(modeladmin, request, queryset):
    """
    """
    opts = modeladmin.model._meta
    app_label = opts.app_label
    
    # Populate modifiable_objects, a data structure of all related objects that will also be deleted.
    modifiable_objects, perms_needed = get_deleted_objects(queryset, opts, request.user, modeladmin.admin_site, levels_to_root=2)

    can_audit = validate_false_paper_have_type(queryset, [enums.FW_PAPER_TYPE, enums.BMW_PAPER_TYPE])
    if can_audit == False:
        messages.error(request, msg_paper_not_belong_fht)
        return None
    paper_st_right = validate_false_paper_status(request, queryset, [enums.FH_PAPER_STATUS_INPUT, enums.FH_PAPER_STATUS_WAIT_AUDIT_1], u'独立复核团队审核')
    if paper_st_right == False:
        return None
    # The user has already confirmed the deletion.
    # Do the deletion and return a None to display the change list view again.    
    if request.POST.get('post'):
        user = request.user
        # 权限判定
        if not has_fh_audit_perm(user) and not has_manage_perm(user):
            raise PermissionDenied
        
        n = queryset.count()
        if n:
            perm = enums.FH_PAPER_STATUS_WAIT_AUDIT_2
            for obj in queryset :
                obj_display = force_unicode(obj)
                if obj.status < perm:
                    from mc import save_paper_audit_status
                    save_paper_audit_status(obj, request.user, perm)
                    
                    obj.status = perm
                    obj.save()
                    
                    # change
                    modeladmin.log_change(request, obj, obj_display)
                else:
                    n -= 1

            modeladmin.message_user(request, u'独立复核审核通过 %(count)d %(items)s 报告.' % {
                "count": n, "items": model_ngettext(modeladmin.opts, n)
            })
        
        # Return None to display the change list page again.
        return None
    
    context = {
        "title": _("Are you sure?"),
        "object_name": force_unicode(opts.verbose_name),
        "modifiable_objects": modifiable_objects,
        'queryset': queryset,
        
        "opts": opts,
        "root_path": modeladmin.admin_site.root_path,
        "app_label": app_label,
        'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
    }
    
    # Display the confirmation page
    return render_to_response('fh_audit_confirmation.html', context, context_instance=template.RequestContext(request))

########################################
# 独立复核终审
def fh_end_audit(modeladmin, request, queryset):
    """
    """
    opts = modeladmin.model._meta
    app_label = opts.app_label
    
    # Populate modifiable_objects, a data structure of all related objects that will also be deleted.
    modifiable_objects, perms_needed = get_deleted_objects(queryset, opts, request.user, modeladmin.admin_site, levels_to_root=2)
    
    can_audit = validate_false_paper_have_type(queryset, [enums.FW_PAPER_TYPE, enums.BMW_PAPER_TYPE])
    if can_audit == False:
        messages.error(request, msg_paper_not_belong_fht)
        return None
    paper_st_right = validate_false_paper_status(request, queryset, [enums.FH_PAPER_STATUS_WAIT_AUDIT_2], u'独立复核团队终审')
    if paper_st_right == False:
        return None
    # The user has already confirmed the deletion.
    # Do the deletion and return a None to display the change list view again.    
    if request.POST.get('post'):
        user = request.user
        # 权限判定
        if not has_fh_end_audit_perm(user) and not has_manage_perm(user):
            raise PermissionDenied
        n = queryset.count()
        passed_papers = []
        if n:
            perm = enums.PAPER_STATUS_FINISH
            for obj in queryset :
                obj_display = force_unicode(obj)
                if obj.status < perm:
                    from mc import save_paper_audit_status
                    save_paper_audit_status(obj, request.user, perm)
                    
                    obj.status = perm
                    obj.save()
                    passed_papers.append(obj)
                    # change
                    modeladmin.log_change(request, obj, obj_display)
                else:
                    n -= 1
            
            modeladmin.message_user(request, u'独立复核终审通过 %(count)d %(items)s 报告.' % {
                "count": n, "items": model_ngettext(modeladmin.opts, n)
            })
            if len(passed_papers) > 0:
                from service.core._report import generate_report_by_paper
                generate_report_by_paper(queryset)
                conflicts_msg = []
                for paper in queryset:
                    no_conflict, diff = paperdiff.do_dealer_paper_diff(paper, user)
#                    if not no_conflict:
#                        conflicts_msg.append(u'%s(FW团队问卷: %s 与 复核团队问卷: %s 比较，产生BMW审核问卷: %s)' % (paper.dealer.name, diff.fw_paper.survey_code, diff.fh_paper.survey_code, diff.final_paper.survey_code))
#                if len(conflicts_msg) > 0:
#                    modeladmin.message_user(request, u'产生问卷差异的经销商及相关问卷信息如下:')
#                    for tmpmsg in conflicts_msg:
#                        modeladmin.message_user(request, tmpmsg)
#                else:
#                    modeladmin.message_user(request, u'并未产生问卷差异.')
        
        # Return None to display the change list page again.
        return None
    
    context = {
        "title": _("Are you sure?"),
        "object_name": force_unicode(opts.verbose_name),
        "modifiable_objects": modifiable_objects,
        'queryset': queryset,
        
        "opts": opts,
        "root_path": modeladmin.admin_site.root_path,
        "app_label": app_label,
        'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
    }
    
    # Display the confirmation page
    return render_to_response('fh_finish_audit_confirmation.html', context, context_instance=template.RequestContext(request))

########################################
# FH取消终审
def fh_cancel_audit(modeladmin, request, queryset):
    """
    """
    opts = modeladmin.model._meta
    app_label = opts.app_label
    
    # Populate modifiable_objects, a data structure of all related objects that will also be deleted.
    modifiable_objects, perms_needed = get_deleted_objects(queryset, opts, request.user, modeladmin.admin_site, levels_to_root=2)
    
    can_audit = validate_false_paper_have_type(queryset, [enums.FW_PAPER_TYPE, enums.BMW_PAPER_TYPE])
    if can_audit == False:
        messages.error(request, msg_paper_not_belong_fht)
        return None
    paper_st_right = validate_false_paper_status(request, queryset, [enums.PAPER_STATUS_FINISH], u'独立复核团队取消终审')
    if paper_st_right == False:
        return None
    # The user has already confirmed the deletion.
    # Do the deletion and return a None to display the change list view again.    
    if request.POST.get('post'):
        user = request.user
        # 权限判定
        if not has_fh_end_audit_perm(user) and not has_manage_perm(user):
            raise PermissionDenied
        
        n = queryset.count()
        if n:
            for obj in queryset :
                obj_display = force_unicode(obj)
                #remove paper FW audit info
                audits = PaperAudit.objects.filter(paper=obj, new_status=obj.status)
                for au in audits:
                    au.delete()
                    
                obj.status = enums.FH_PAPER_STATUS_WAIT_AUDIT_2
                obj.save()
                
                # change
                modeladmin.log_change(request, obj, obj_display)

            modeladmin.message_user(request, u'成功 取消 %(count)d %(items)s 复核终审.' % {
                "count": n, "items": model_ngettext(modeladmin.opts, n)
            })
        
        # Return None to display the change list page again.
        return None
    
    context = {
        "title": _("Are you sure?"),
        "object_name": force_unicode(opts.verbose_name),
        "modifiable_objects": modifiable_objects,
        'queryset': queryset,
        
        "opts": opts,
        "root_path": modeladmin.admin_site.root_path,
        "app_label": app_label,
        'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
    }
    
    # Display the confirmation page
    return render_to_response('fh_cancel_audit_confirmation.html', context, context_instance=template.RequestContext(request))


########################################
# 批量生成得分
def save_all(modeladmin, request, queryset):
    """
    """
    opts = modeladmin.model._meta
    app_label = opts.app_label
    
    # Populate modifiable_objects, a data structure of all related objects that will also be deleted.
    modifiable_objects, perms_needed = get_deleted_objects(queryset, opts, request.user, modeladmin.admin_site, levels_to_root=2)

#    can_audit = validate_false_paper_have_type(queryset, [enums.BMW_PAPER_TYPE])
#    if can_audit == False:
#        messages.error(request, u'BMW终审问卷不能操作')
#        return None
    
    # The user has already confirmed the deletion.
    # Do the deletion and return a None to display the change list view again.    
    if request.POST.get('post'):
        user = request.user
        # 权限判定
        #督导，终审，管理员可用
        if not has_fh_end_audit_perm(user) and not has_end_audit_perm(user) and not has_manage_perm(user) and not has_dd_audit_perm(user):
            raise PermissionDenied
        
        n = queryset.count()
        if n:
            perm = enums.FH_PAPER_STATUS_WAIT_AUDIT_2
            for obj in queryset :
                obj_display = force_unicode(obj)
                #统计得
                from service.core._report import calculate_paper_total_score
                calculate_paper_total_score(obj)
                obj.save()
                # change
                modeladmin.log_change(request, obj, obj_display)

            modeladmin.message_user(request, u'保存 %(count)d %(items)s 报告.' % {
                "count": n, "items": model_ngettext(modeladmin.opts, n)
            })
        
        # Return None to display the change list page again.
        return None
    
    context = {
        "title": _("Are you sure?"),
        "object_name": force_unicode(opts.verbose_name),
        "modifiable_objects": modifiable_objects,
        'queryset': queryset,
        
        "opts": opts,
        "root_path": modeladmin.admin_site.root_path,
        "app_label": app_label,
        'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
    }
    
    # Display the confirmation page
    return render_to_response('save_all_confirmation.html', context, context_instance=template.RequestContext(request))

########################################
# 批量生成得分
def gen_report_bentch(modeladmin, request, queryset):
    """
    """
    opts = modeladmin.model._meta
    app_label = opts.app_label
    
    # Populate modifiable_objects, a data structure of all related objects that will also be deleted.
    modifiable_objects, perms_needed = get_deleted_objects(queryset, opts, request.user, modeladmin.admin_site, levels_to_root=2)

#    can_audit = validate_false_paper_have_type(queryset, [enums.BMW_PAPER_TYPE, enums.FH_PAPER_TYPE])
#    if can_audit == False:
#        messages.error(request, u'FW团队终审问卷才能生成单店报告')
#        return None
    
    # The user has already confirmed the deletion.
    # Do the deletion and return a None to display the change list view again.    
    if request.POST.get('post'):
        user = request.user
        # 权限判定
        #督导，终审，管理员可用
        if not has_fh_end_audit_perm(user) and not has_end_audit_perm(user) and not has_manage_perm(user) and not has_dd_audit_perm(user):
            raise PermissionDenied
        
        n = queryset.count()
        if n:
            from mc import gen_report
            perm = enums.PAPER_STATUS_FINISH
            for obj in queryset :
                if obj.status == perm:
                    obj_display = force_unicode(obj)
                    #统计得
                    gen_report(obj, user)
                    # change
                    modeladmin.log_change(request, obj, obj_display)
                else:
                    n -= 1
            modeladmin.message_user(request, u'生成 %(count)d %(items)s EXCEL单店报告.' % {
                "count": n, "items": model_ngettext(modeladmin.opts, n)
            })
        
        # Return None to display the change list page again.
        return None
    
    context = {
        "title": _("Are you sure?"),
        "object_name": force_unicode(opts.verbose_name),
        "modifiable_objects": modifiable_objects,
        'queryset': queryset,
        
        "opts": opts,
        "root_path": modeladmin.admin_site.root_path,
        "app_label": app_label,
        'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
    }
    
    # Display the confirmation page
    return render_to_response('gen_report_bentch_confirmation.html', context, context_instance=template.RequestContext(request))

qc1_audit.short_description = u'QC一审'
qc2_audit.short_description = u'QC二审'
qc3_audit.short_description = u'QC三审'
qc3_re_audit.short_description = u'退回QC三重审'
dd_audit.short_description = u'督导审核'
yj_audit.short_description = u'研究审核'
end_audit.short_description = u'终审确认'
cancel_audit.short_description = u'取消终审'
fh_audit.short_description = u'独立复核团队审核'
fh_end_audit.short_description = u'独立复核团队终审'
fh_cancel_audit.short_description = u'独立复核团队取消终审'
save_all.short_description = u'批量保存'
gen_report_bentch.short_description = u'批量生成EXCEL单店报告'
