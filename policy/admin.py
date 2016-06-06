# -- encoding=utf-8 --
from django.contrib import admin
from django import forms
from django.utils.translation import ugettext_lazy as _
from models import AuthorizedIp

class AuthorizedIpAdmin(admin.ModelAdmin):
    list_display = ('desc', 'ip', 'enable', 'createdby', 'created')
    readonly_fields = ("created",)
    list_editable = ('enable',)
    fieldsets = (
        (None, {'fields': ('ip', 'desc', 'enable',)}),
    )
    list_filter = ('ip', 'desc',)
    def save_model(self, request, obj, form, change):
        obj.createdby = request.user
        obj.save()

admin.site.register(AuthorizedIp, AuthorizedIpAdmin)
