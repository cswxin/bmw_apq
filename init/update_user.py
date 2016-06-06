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
    Maxinsight1_password = '497886'
#    Maxinsight1_password = get_random_password()
    print 'Maxinsight1_password:', Maxinsight1_password
    update_password('Maxinsight1', Maxinsight1_password)
    
    Maxinsight2_password = '190116'
#    Maxinsight2_password = get_random_password()
    print 'Maxinsight2_password:', Maxinsight2_password
    update_password('Maxinsight2', Maxinsight2_password)
    
    AFS_password = '223323'
#    AFS_password = get_random_password()
    print 'AFS_password:', AFS_password
    update_password('AFS', AFS_password)
    
    AFS_B_password = '034818'
#    AFS_B_password = get_random_password()
    print 'AFS_B_password:', AFS_B_password
    update_password('AFS_B', AFS_B_password)
    
    #ycf 可能区域英文名为空
    region_list = [u'东区', u'南区', u'西区', u'北区', u'东南区']
    #region_list = ['East','South','West','North','SouthEast']
    for region in region_list:
#        if region == 'East':
#            region_password = '377025'
#            xq_password = '720344'
#        if region == 'South':
#            region_password = '668516'
#            xq_password = '880489'
#        if region == 'West':
#            region_password = '087629' 
#            xq_password = '157584'
#        if region == 'North':
#            region_password = '030586'
#            xq_password = '521588' 
#        if region == 'SouthEast':
#            region_password = '062506'
#            xq_password = '431169'
        if region == u'东区':
            region_en = 'East'
            region_password = '876223'
            xq_password = '862747'
        if region == u'南区':
            region_en = 'South'
            region_password = '536449'
            xq_password = '713423'
        if region == u'西区':
            region_en = 'West'
            region_password = '844557'
            xq_password = '057011'
        if region == u'北区':
            region_en = 'North'
            region_password = '888046'
            xq_password = '527889' 
        if region == u'东南区':
            region_en = 'SouthEast'
            region_password = '998683'
            xq_password = '826576'   
#        region_password = get_random_password()
        print '%s_password:' % region_en, region_password
        update_password(region_en, region_password)
        region_dealer = Dealer.objects.get(name_cn=region)
        #region_dealer = Dealer.objects.get(name_en=region)
        xq_list = Dealer.objects.filter(xq_parent=region_dealer)
#        xq_password = get_random_password()
#        xq_password = '123456'
        print '%s_xq_password:' % region_en, xq_password
        for xq in xq_list:
            update_password(xq.name, xq_password)

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
    
