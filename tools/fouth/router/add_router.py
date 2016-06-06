#encoding:utf-8
'''
Created on 2012-3-8

@author: junhua
'''

import os, sys
sys.path.insert(0, os.path.abspath(os.curdir))
from django.db.transaction import commit_on_success
from django.contrib.auth.models import User, Group
from mc import get_cur_input_term
from django.conf import settings
from mc.models import Router
from userpro import enums
from userpro.models import UserProfile, UserPermission
import xlrd
from utils.xpinyin import Pinyin
pinyin = Pinyin()

@commit_on_success
def add_router():
    xlsfile = os.path.join(settings.RESOURCES_ROOT, u'fouth/router/路线图和评估员信息_1029.xls')
    book = xlrd.open_workbook(xlsfile)
    term = get_cur_input_term()
     
    #设置所有访问员为不活跃
    g = Group.objects.get(name=enums.FW_INPUT_GROUP)
    users = User.objects.filter(groups__in=[g])
    for u in users:
        u.is_staff = False
        u.is_active = False
        u.save()
        print u.username
        
    #路线
    sh = book.sheet_by_index(0)
    print sh.name, sh.nrows, sh.ncols
    for rx in range(sh.nrows):
        texts = sh.row_values(rx)
        router, create = Router.objects.get_or_create(name=texts[0].strip(), term=term)
        texts.remove(texts[0])
        while '' in texts:
            texts.remove('')
        print router.name, texts
        router.citys = '-'.join(texts)
        router.save()

    #访问员
    #后台：只能在后台录入问卷。
    #前台：没有权限登录前台。
    sh = book.sheet_by_index(1)
    print sh.name, sh.nrows, sh.ncols
    for rx in range(1, sh.nrows):
        texts = sh.row_values(rx)
        username = texts[0].strip()
        password = '%s' % int(texts[2])
        uname = username
        user, create = User.objects.get_or_create(username=uname)
        user.set_password(password)
        user.is_staff = True
        user.is_active = True
        user.first_name = '%s %s' % (texts[1], username)
        user.groups = [g, ]
        user.save()
        print user.first_name
        
        up, create = UserProfile.objects.get_or_create(user=user)
        p = UserPermission.objects.get(name=enums.FW_INPUT_PERMISSION)
        up.user_permissions = [p, ]
        up.save()

def add_routers():
    add_router()

if __name__ == '__main__':
    add_routers()
