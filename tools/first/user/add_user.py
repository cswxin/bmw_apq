#encoding:utf-8
import os, sys
sys.path.insert(0, os.path.abspath(os.curdir))

from django.db.transaction import commit_on_success
from django.contrib.auth.models import User, Group, Permission
from mc.models import Dealer
from userpro.models import UserPermission, UserProfile, LoginLogout
import xlrd
import random
from userpro.enums import *
import sys, os
from django.conf import settings
from userpro.enums import MC_PERMISSIONS

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
    dealer_nation = Dealer.objects.get_or_create(name=u'全国', name_cn=u'全国', name_en='Nation', abbr_cn=u'全国', has_child=True, level=0)[0]
    
#    _add_user('admin', u'admin', 'smk', [MAN_GROUP], [SHOW_ALL_PAGE,SHOW_NO_RUN_PAGE,],dealer_nation)
#    
#    _add_user('Grace', u'Grace', '123456', [NATION_GROUP], [SHOW_ALL_PAGE,SHOW_NO_RUN_PAGE,],dealer_nation)
    password = str(random.random())[2:8]
    print password
    _add_user('Nicole', u'Nicole', password, [NATION_GROUP], [SHOW_ALL_PAGE,SHOW_NO_RUN_PAGE,],dealer_nation)
    
#    _add_user('AFS', u'AFS', '123456', [NATION_GROUP], [SHOW_ALL_PAGE,SHOW_NO_RUN_PAGE,],dealer_nation)
#    
#    _add_user('AFS_B', u'AFS_B', '123456', [NATION_GROUP], [SHOW_ALL_PAGE,SHOW_NO_RUN_PAGE,],dealer_nation)
#    
#    _add_user('Maxinsight1', u'Maxinsight1', '123456', [MAN_GROUP], [SHOW_ALL_PAGE,SHOW_NO_RUN_PAGE,],dealer_nation)
#    
#    _add_user('Maxinsight2', u'Maxinsight2', '123456', [MAN_GROUP], [SHOW_ALL_PAGE,SHOW_NO_RUN_PAGE,],dealer_nation)
    
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
        up.dealer = dealer
        up.save()   
        
@commit_on_success
def add_permissions():
#    UserPermission.objects.all().delete()
    for pname in MC_PERMISSIONS:
        p, create = UserPermission.objects.get_or_create(name=pname)
        print p.name

def add_users():
#    add_group()#添加组
#    add_permissions()
    add_user()#添加user
    
if __name__ == '__main__':
    add_users()
