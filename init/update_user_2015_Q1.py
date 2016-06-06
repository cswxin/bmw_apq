#encoding:utf-8
import csv
import os, sys
sys.path.insert(0, os.path.abspath(os.curdir))

from django.conf import settings
from django.db.transaction import commit_on_success
from django.contrib.auth.models import User
import random
from mc.models import Dealer

def get_random_password():
    password = str(random.random())[2:8]
    return password

def update_password(username, password):
    u, create = User.objects.get_or_create(username=username)
    u.first_name = username
    if create:
        print 'create:', username
    u.set_password(password)
    u.save()

def update_user():

    AFS_password = '223323'
#    AFS_password = get_random_password()
    print 'AFS_password:', AFS_password
    update_password('AFS', AFS_password)

    AFS_B_password = '034818'
#    AFS_B_password = get_random_password()
    print 'AFS_B_password:', AFS_B_password
    update_password('AFS_B', AFS_B_password)

    Serena_password = '123456'
    print 'Serena_password', Serena_password
    update_password('Serena', Serena_password)

    #ycf 可能区域英文名为空
    region_list = [u'东区', u'南区', u'西区', u'北区', u'东南区']
    for region in region_list:
        if region == u'东区':
            region_en = 'East'
            region_password = '901357'
        if region == u'南区':
            region_en = 'South'
            region_password = '246048'
        if region == u'西区':
            region_en = 'West'
            region_password = '713084'
        if region == u'北区':
            region_en = 'North'
            region_password = '758361'
        if region == u'东南区':
            region_en = 'SouthEast'
            region_password = '302769'
        #region_password = get_random_password()#ycf  大区密码先随机让大区不能登录
        print '%s_password:' % region_en, region_password
        update_password(region_en, region_password)

def add_dealer(name, name_cn, parent, xq_parent):
    dealer = Dealer.objects.get_or_create(name=name, name_cn=name_cn, level=4)[0]
    dealer.abbr_cn = name_cn
    dealer.has_child = True
    dealer.parent = parent
    dealer.xq_parent = xq_parent
    dealer.save()
    return dealer

def add_no_dealer_user():
    parent = Dealer.objects.get_or_create(id=1)[0]
    North = Dealer.objects.get_or_create(name_en='North')[0]
    East = Dealer.objects.get_or_create(name_en='East')[0]
    South = Dealer.objects.get_or_create(name_en='South')[0]

    d108 = add_dealer('108', 'Kevin Guo', parent, North)

    d202 = add_dealer('202', 'John Chen', parent, East)
    d203 = add_dealer('203', 'Ming Li', parent, East)
    d209 = add_dealer('209', 'Terry Zhou', parent, East)

    d310 = add_dealer('310', 'Daisy Sun', parent, South)

if __name__ == '__main__':
    update_user()
#    add_no_dealer_user()

