# -- encoding=utf-8 --
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from models import UserProfile, UserPermission, LoginLogout

import permfilter
from permfilter import PERMS_VAR, PermsFilterSpec

from django.utils.encoding import smart_unicode
from service.core._user import get_dealer_by_user

from django.contrib.auth import forms as useforms
from django import forms

from django.utils.translation import ugettext_lazy as _
from django.utils.http import int_to_base36

class UserCreationForm2(useforms.UserCreationForm):
    """
    A form that creates a user, with no privileges, from the given username and password.
    """
    username = forms.RegexField(label=_("Username"), max_length=30, regex=r'^\.*',
        help_text=_("Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only."),
        error_messages={'invalid': _("This value may contain only letters, numbers and @/./+/-/_ characters.")})
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"), widget=forms.PasswordInput,
        help_text=_("Enter the same password as above, for verification."))

class UserChangeForm2(useforms.UserChangeForm):
    username = forms.RegexField(label=_("Username"), max_length=30, regex=r'^\.*',
        help_text=_("Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only."),
        error_messages={'invalid': _("This value may contain only letters, numbers and @/./+/-/_ characters.")})

from django.contrib.admin.views.main import ChangeList
class PermsChangeList(ChangeList):
    def get_results(self, request):
        qs = self.query_set
        if self.pid:            
            wheresql = 'auth_user.id=userpro_userprofile.user_id and userpro_userprofile_user_permissions.userpermission_id=%d and userpro_userprofile_user_permissions.userprofile_id=userpro_userprofile.id' % self.pid
            tables = ['userpro_userprofile', 'userpro_userprofile_user_permissions']
            qs = qs.extra(where=[wheresql, ], tables=tables)
            
        qs = qs.filter(is_active=True)
        self.query_set = qs
        
        return super(PermsChangeList, self).get_results(request)
    
    def get_query_set(self):
        self.pid = 0
        if PERMS_VAR in self.params:
            self.pid = int(self.params[PERMS_VAR])
            del self.params[PERMS_VAR]
        
        return super(PermsChangeList, self).get_query_set()
    
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    fk_name = 'user'
    max_num = 1
    filter_horizontal = ('user_permissions',)
    list_filter = ('user_permissions',)
    
    fieldsets = (
        (None, {'fields': ('user_permissions', 'dealer')}),
        )

class CustomUserAdmin(UserAdmin):
    #change_list_template = ''
    
    inlines = [UserProfileInline, ]
    
    list_display = ('username', 'first_name', 'login_count', 'last_login', 'group_name', 'permission_name', 'is_staff', 'city_name')
    list_filter = ('groups', 'user_permissions',)
    search_fields = ('username', 'first_name', 'last_name')
    ordering = ['-id']
    filter_horizontal = ('groups',)
    
    def operate_name(self, obj):
        name = u'操作权限'
        return name
    
    form = UserChangeForm2
    add_form = UserCreationForm2
    
    operate_name.short_description = u'操作权限'
    operate_name.verbose_name = u'操作权限'
    operate_name.perms_filter_spec = True
    operate_name.allow_tags = True
    
    def city_name(self, obj):
        dealer = get_dealer_by_user(obj)
        if dealer:
            return dealer.city_cn
        return ''
    
    city_name.short_description = u'城市'
    city_name.verbose_name = u'城市'
    city_name.allow_tags = True
    
    
    fieldsets = (
        (None, {'fields': ('username', 'last_name', 'first_name', 'password', 'is_staff', 'groups',)}),
        )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'last_name', 'first_name', 'password1', 'password2', 'is_staff', 'groups',)}
        ),
    )
    
    def get_changelist(self, request, **kwargs):
        return PermsChangeList
    
    def login_count(self, obj):
        up, create = UserProfile.objects.get_or_create(user=obj)
        return up.login_count
    
    def group_name(self, obj):
        names = []
        gs = obj.groups.all()
        for g in gs:
            names.append(g.name)
        
        return u','.join(names)
    
    def permission_name(self, obj):
        names = []
        up, create = UserProfile.objects.get_or_create(user=obj)
        gs = up.user_permissions.all()
        for g in gs:
            names.append(g.name)
        
        return u','.join(names)
    
    def validate(cls, model):
        pass
    
    login_count.short_description = u'登录次数'
    group_name.short_description = u'所属用户组'
    permission_name.short_description = u'用户权限'
    #is_staff.short_description = u'是否使用'
    
    def save_model(self, request, obj, form, change):
        from mcview.decorator import cached
        @cached('user_key_%s' % (obj.username))
        def __save(obj, refresh=False):
            obj.save()
            return obj
        __save(obj, refresh=True)
        
    
    
    def changelist_view_old(self, request, extra_context=None):
        select_val = request.GET.get(PERMS_VAR, '')
        
        perm_choices = []
        item = UserPermission()
        item.name = u'全部'
        item.href = '?'
        if not select_val:
            item.selected = True
        
        perm_choices.append(item)
        ups = UserPermission.objects.all().order_by('id')
        for p in ups:
            p.href = '?%s=%d' % (PERMS_VAR, p.id)
            if select_val == smart_unicode(p.id):
                p.selected = True
            
            perm_choices.append(p)
            
        if not extra_context:
            extra_context = {}
        extra_context['perm_choices'] = perm_choices
        return super(CustomUserAdmin, self).changelist_view(request, extra_context)
    
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

class LoginLogoutAdmin(admin.ModelAdmin):
    list_display = ('user', 'ip', 'created',)
    fieldsets = (
        (None, {'fields': ()}),
    )
    
    ordering = ['id', ]
    #def save_model(self, request, obj, form, change):
    #    obj.user = request.user
    #    obj.save()

admin.site.register(LoginLogout, LoginLogoutAdmin)

