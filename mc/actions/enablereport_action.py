#!/usr/bin/python
# coding=utf-8

from django import template
from django.core.exceptions import PermissionDenied
from django.contrib.admin import helpers
from django.contrib.admin.util import get_deleted_objects, model_ngettext
from django.shortcuts import render_to_response
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext_lazy, ugettext as _

from mc.models import Report
from service.core._user import has_manage_perm

########################################
# 公开报告
def enablereport(modeladmin, request, queryset):
    """
    """
    opts = modeladmin.model._meta
    app_label = opts.app_label
    
    # Populate modifiable_objects, a data structure of all related objects that will also be deleted.
    modifiable_objects, perms_needed = get_deleted_objects(queryset, opts, request.user, modeladmin.admin_site, levels_to_root=2)

    # The user has already confirmed the deletion.
    # Do the deletion and return a None to display the change list view again.    
    if request.POST.get('post'):
        user = request.user
        # 权限判定
        if not has_manage_perm(user):
            raise PermissionDenied
        
        n = queryset.count()
        if n:
            for obj in queryset :
                obj_display = force_unicode(obj)
                obj.is_public = True
                obj.save()
                
                # change
                modeladmin.log_change(request, obj, obj_display)

            modeladmin.message_user(request, u'成功 公开 %(count)d %(items)s 报告.' % {
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
    return render_to_response('enablereport_confirmation.html', context, context_instance=template.RequestContext(request))

#
########################################
# 屏蔽报告
def disablereport(modeladmin, request, queryset):
    """
    """
    opts = modeladmin.model._meta
    app_label = opts.app_label
    
    # Populate modifiable_objects, a data structure of all related objects that will also be deleted.
    modifiable_objects, perms_needed = get_deleted_objects(queryset, opts, request.user, modeladmin.admin_site, levels_to_root=2)

    # The user has already confirmed the deletion.
    # Do the deletion and return a None to display the change list view again.    
    if request.POST.get('post'):
        user = request.user
        # 权限判定
        if not has_manage_perm(user):
            raise PermissionDenied
        
        n = queryset.count()
        if n:
            for obj in queryset :
                obj_display = force_unicode(obj)
                obj.is_public = False
                obj.save()
                
                # change
                modeladmin.log_change(request, obj, obj_display)

            modeladmin.message_user(request, u'成功 屏蔽 %(count)d %(items)s 报告.' % {
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
    return render_to_response('disablereport_confirmation.html', context, context_instance=template.RequestContext(request))

enablereport.short_description = u'公开报告'
disablereport.short_description = u'屏蔽报告'
