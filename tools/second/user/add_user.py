#encoding:utf-8
import os, sys
sys.path.insert(0, os.path.abspath(os.curdir))

from django.db.transaction import commit_on_success
from django.contrib.auth.models import User, Group, Permission
from mc.models import Dealer
from userpro.models import UserPermission, UserProfile, LoginLogout
import xlrd
from userpro.enums import *

import sys, os
from django.conf import settings

@commit_on_success
def add_group():
#    Group.objects.all().delete()
#    Permission.objects.all().delete()
    for gname, perdict in MC_GROUPS:
        g, create = Group.objects.get_or_create(name=gname)
        ps = []
        for key, perm in perdict.items():
            perms = []
            if perm == 'all':
                perms.append(u'Can add %s' % key)
                perms.append(u'Can delete %s' % key)
                perms.append(u'Can change %s' % key)
            else:
                pnames = perm.split(',')
                for pname in pnames:
                    perms.append(u'Can %s %s' % (pname, key))
            
            for pm in perms:
                print pm
                p = Permission.objects.get(name=pm)
                ps.append(p)
        
        g.permissions = ps
        g.save()

@commit_on_success
def add_nation_dealer():
    d, create = Dealer.objects.get_or_create(name=u'全国')
    d.name_cn = u'全国'
    d.has_child = True
    d.level = 0
    d.save()
    print d.name_cn

@commit_on_success
def add_user():
#    User.objects.all().delete()
#    UserProfile.objects.all().delete()
#    LoginLogout.objects.all().delete()
    xlsfile = os.path.join(settings.RESOURCES_ROOT, u'second/user/项目组人员ID号20120523.xls')
    book = xlrd.open_workbook(xlsfile)
    
    sh = book.sheet_by_index(0)
    print sh.name, sh.nrows, sh.ncols
    for rx in range(1, sh.nrows):
        texts = sh.row_values(rx)
        perm_des = texts[0]
        first_name = texts[1].strip()
        username = texts[2].strip()
        password = ('%d' % texts[3]).strip()
        groups = []
        perms = []
        print username, password
        if perm_des.find(u'QC一审') != -1:
            #后台：只能在后台点击Action的“QC一审”。还可以对评估员录入的问卷进行网上修改。
            #前台：没有权限登录前台。
            groups = [ FW_AUDIT_GROUP ]
            perms = [FW_BEGIN_AUDIT_PERMISSION]
        elif perm_des.find(u'QC二审') != -1:
            #后台：只能在后台点击Action的“QC二审”。还可以对经过一审的问卷进行网上修改。
            #前台：没有权限登录前台。
            groups = [FW_AUDIT_GROUP]
            perms = [FW_QC_AUDIT_PERMISSION]
        elif perm_des.find(u'QC三审') != -1:
            #后台:只能在后台点击Action的QC三审。还可以对经过二审的问卷进行网上修改。
            #前台：没有权限登录前台。
            groups = [FW_AUDIT_GROUP]
            perms = [FW_QC_AUDIT_PERMISSION2]
        elif perm_des.find(u'督导审核') != -1:
            #后台：在后台可以点击Action的“督导审核”和“删除问卷”。还可以对经过三审的问卷进行网上修改。
            #前台：可以进入“项目概览” 、“问卷问与答”、“执行进度”。
            groups = [FW_DUDAO_GROUP]
            perms = [FW_AREA_AUDIT_PERMISSION]
        elif perm_des.find(u'研究审核') != -1:
            #后台：在后台可以点击Action的“研究审核”、“终审确认”、“取消终审”、“公开报告”、“屏蔽报告”、“删除问卷”。还能够修改问卷。
            #前台：可以进入前台任何地方。可以使用前台的任何功能。
            groups = [FW_AUDIT_GROUP]
            perms = [FW_AUDIT_PERMISSION, FW_END_AUDIT_PERMISSION, SHOW_ALL_PAGE]
        elif perm_des.find(u'独立复核') != -1:
            #后台：在后台录入问卷。还可以点击Actio的“独立复核团队审核”、“独立复核团队终审”、“独立复核团队取消终审”，“删除问卷”。还可以修改问卷。
            #前台：没有权限登录前台。
            groups = [FH_INPUT_GROUP, FH_AUDIT_GROUP]
            perms = [FH_INPUT_PERMISSION, FH_AUDIT_PERMISSION, FH_END_AUDIT_PERMISSION]
        elif perm_des.find(u'BMW01') != -1:
            #后台：没有登录后台的权限。
            #前台：可以登录和使用前台的任何界面。
            groups = [BMW_GROUP]
            perms = [BMW_AUDIT_PERMISSION, SHOW_ALL_PAGE]
        elif perm_des.find(u'BMW02') != -1:
            #后台：没有登录后台的权限。
            #前台：除了“执行进度”版块和“经销商的登陆次数和时间”功能之外，其他界面都可以使用。
            groups = [BMW_GROUP]
            perms = [SHOW_NO_RUN_PAGE]
        elif perm_des.find(u'翻译') != -1:
            #后台：只能填写问卷“否”和“不涉及”的中文和英文翻译。
            #前台：可以浏览“项目概览”，“问卷问与答”，“执行进度”。还有经销商单店分析 Dealer Analysis 中的“经销商单店报告 Dealer Report”。

            groups = [FW_TRAN_GROUP]
            perms = [TRAN_PERMISSION]
        elif perm_des.find(u'管理员') != -1:
            #可以进入前台和后台的任何界面，拥有前台和后台的所有权限。
            groups = [MAN_GROUP, FW_AUDIT_GROUP, FH_AUDIT_GROUP]
            perms = [MANAGER_PERMISSION, SHOW_ALL_PAGE]
        _add_user(username, first_name, password, groups, perms)
        print  username, first_name
    
#    _add_user('gfk01', u'访问员', '123456', [FW_INPUT_GROUP], [FW_INPUT_PERMISSION])
#    _add_user('gfk02', u'QC一审', '123456', [FW_AUDIT_GROUP], [FW_BEGIN_AUDIT_PERMISSION])
#    _add_user('gfk03', u'QC二审', '123456', [FW_AUDIT_GROUP], [FW_QC_AUDIT_PERMISSION])
#    _add_user('gfk04', u'QC三审', '123456', [FW_AUDIT_GROUP], [FW_QC_AUDIT_PERMISSION2])
#    
#    _add_user('gfk05', u'宋露露', '123456', [FW_DUDAO_GROUP], [FW_AREA_AUDIT_PERMISSION])
#    _add_user('gfk06', u'研究部', '123456', [FW_AUDIT_GROUP], [FW_AUDIT_PERMISSION, FW_END_AUDIT_PERMISSION, SHOW_ALL_PAGE])
    
    

def _add_user(username, firstname, password, groups, perm_list, dealer=None):
    u, create = User.objects.get_or_create(username=username)
    u.first_name = firstname
    u.set_password(password)
    u.is_staff = True
    if groups:
        grps = []
        for gname in groups:
            g, create = Group.objects.get_or_create(name=gname)
            grps.append(g)
    u.groups = grps
    u.save()
    
    if perm_list:
        up, create = UserProfile.objects.get_or_create(user=u)
        perms = []
        for pername in perm_list:
            per, create = UserPermission.objects.get_or_create(name=pername)
            perms.append(per)
        up.user_permissions = perms
        up.save()
    if dealer:
        up, create = UserProfile.objects.get_or_create(user=u)
        up.user_dealers.add(dealer)
        up.save()   
@commit_on_success
def add_permissions():
#    UserPermission.objects.all().delete()
    for pname in MC_PERMISSIONS:
        p, create = UserPermission.objects.get_or_create(name=pname)
        print p.name

def add_users():
    #add_group()#添加组
    #add_permissions()
    add_user()#添加user
    
if __name__ == '__main__':
    add_users()
