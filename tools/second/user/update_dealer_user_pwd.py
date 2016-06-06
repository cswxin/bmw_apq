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
def update_user():
#    User.objects.all().delete()
#    UserProfile.objects.all().delete()
#    LoginLogout.objects.all().delete()
    dealergroup = Group.objects.get(name=u'经销商')
    dealer_users = User.objects.filter(groups__in=[dealergroup, ]) 
    for u in dealer_users:
        u.set_password('654321')
        u.save()
        print u.username
    

def update_users():
    update_user()#添加user
    
if __name__ == '__main__':
    update_users()
