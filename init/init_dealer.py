#encoding:utf-8
import csv
import os, sys
sys.path.insert(0, os.path.abspath(os.curdir))

from django.conf import settings
from django.db.transaction import commit_on_success
from django.contrib.auth.models import User, Group
from mc.models import Dealer, DealerType
from service.core._term import get_cur_input_term
from userpro.models import UserProfile, UserPermission
from userpro.enums import *
import xlrd

def split_str(mystr):
    en = ''
    cn = ''
    for s in mystr:
        if ord(s) > 127 and s not in [u'’',u'‘']:
            cn += s
        else:
            en += s
    return cn,en

@commit_on_success
def add_dealertype(name):
    dt = DealerType.objects.get_or_create(name_cn=name)[0]
    dt.name_en = name
    dt.save()
    return dt
    
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
    
#创建一个用户
def _create_user(username, groupname):
    if not username:
        return None
    
    u, create = User.objects.get_or_create(username=username)
    g, create = Group.objects.get_or_create(name=groupname)
    u.groups.add(g)
    
    password = '123456'
    u.set_password(password)
    u.is_staff = True
    u.save()
    return u

def save_dealer_bmw(sh, dealer_nation, dealer_dt, dt, term):
    for rx in range(1, sh.nrows):
        texts = sh.row_values(rx)
        
        dealer_code = texts[0]
        if isinstance(dealer_code, (int, float)):
            dealer_code = '%s' % int(dealer_code)
        if not dealer_code:
            continue
        name = texts[3].strip().replace('\n', '')
        name_cn,name_en = split_str(name)
        abbr_cn = texts[1].strip()
#        addr = texts[2].strip()
#        website = texts[3].strip()
#        tel = texts[4]
#        if hasattr(tel, 'strip'):
#            tel = tel.strip()
        abbr_en = texts[2].strip()
        
        area = texts[6].strip().replace('\n', '')
        area_cn,area_en = split_str(area)
        province = texts[5].strip().replace('\n', '')
        province_cn,province_en = split_str(province)
        city = texts[4].strip().replace('\n', '')
        city_cn,city_en = split_str(city)
        
        jt_code = texts[9].strip()
        jt_name_cn = texts[8].strip()
        jt_name_en = texts[7].strip()
        
        xq_code = texts[10]
        if isinstance(xq_code, (int, float)):
            xq_code = '%s' % int(xq_code)
        xq_name_cn = texts[11].strip()
        
        new_old = texts[12].strip()
        
        if None in [area, province, city, dealer_code]:
            print u"第%s行有错误" % (rx + 1)
            continue
        
        #区域
        areadealer, create = create_dealer(area_cn, area_cn, area_cn, True, None, name_en=area_en, parent=dealer_nation, sf_parent=dealer_nation, xq_parent=dealer_nation, level=1)
        _add_user(area_en, area_en, '123456', [REGION_GROUP], [SHOW_ALL_PAGE], areadealer)
        #省份
        provincedealer, create = create_dealer(province_cn, province_cn, province_cn, True, None, name_en=province_en, province_cn=province_cn, province_en=province_en, parent=areadealer, sf_parent=areadealer, level=5)
        #城市
        citydealer, create = create_dealer(city_cn, city_cn, city_cn, True, None, name_en=city_en, province_cn=province_cn, province_en=province_en, city_cn=city_cn, city_en=city_en, parent=areadealer, sf_parent=provincedealer, level=2)
        #集团
        jtdealer = None
        if jt_code:
            jtdealer, create = create_dealer(jt_code, jt_name_cn, jt_name_cn, True, None, name_en=jt_name_en, parent=dealer_nation, jt_parent=dealer_nation, level=6)
        #小区
        xqdealer = None
        if xq_code:
            xqdealer, create = create_dealer(xq_code, xq_name_cn, xq_name_cn, True, None, parent=dealer_nation,jt_parent=None, xq_parent=areadealer, level=4)
            _add_user(xq_code, xq_code, '123456', [AREA_GROUP], [SHOW_ALL_PAGE], xqdealer)
        #create_dealer(code, name_cn, abbr_cn, has_child, dealertype, name_en=None, abbr_en=None, province_cn=None, city_cn=None, address=None, tel=None, level=None):        
        #经销商
        d, create = create_dealer(dealer_code, name_cn, abbr_cn, False, dt, name_en=name_en, abbr_en=abbr_en, province_cn=province_cn, province_en=province_en, city_cn=city_cn, city_en=city_en, new_old=new_old, parent=citydealer, jt_parent=jtdealer, xq_parent=xqdealer, sf_parent=citydealer, dt_parent=dealer_dt, level=3)
        term.dealers.add(d)
        if create:
            _add_user(dealer_code, dealer_code, dealer_code, [DEALER_GROUP], [SHOW_ALL_PAGE], d)

def save_dealer_mini(sh, dealer_nation, dealer_dt, dt, term):
    for rx in range(1, sh.nrows):
        texts = sh.row_values(rx)
        
        dealer_code = texts[0]
        if isinstance(dealer_code, (int, float)):
            dealer_code = '%s' % int(dealer_code)
        if not dealer_code:
            continue
        name_cn = texts[6].strip()
        name_en = texts[7].strip()
        abbr_cn = texts[5].strip()
#        addr = texts[6].strip()
#        website = texts[7].strip()
#        tel = texts[8]
#        if hasattr(tel, 'strip'):
#            tel = tel.strip()
        abbr_en = texts[4].strip()
        
        area = texts[1].strip().replace('\n', '')
        area_cn,area_en = split_str(area)
        province = texts[2].strip().replace('\n', '')
        province_cn,province_en = split_str(province)
        city = texts[3].strip().replace('\n', '')
        city_cn,city_en = split_str(city)
        
        xq_code = texts[9]
        if isinstance(xq_code, (int, float)):
            xq_code = '%s' % int(xq_code)
        xq_name_cn = texts[10].strip()
        
        new_old = texts[14].strip()
        
        if None in [area, province, city, dealer_code]:
            print u"第%s行有错误" % (rx + 1)
            continue
        
        #区域
        areadealer, create = create_dealer(area_cn, area_cn, area_cn, True, None, name_en=area_en, parent=dealer_nation, sf_parent=dealer_nation, xq_parent=dealer_nation, level=1)
        _add_user(area_en, area_en, '123456', [REGION_GROUP], [SHOW_ALL_PAGE], areadealer)
        #省份
        provincedealer, create = create_dealer(province_cn, province_cn, province_cn, True, None, name_en=province_en, province_cn=province_cn, province_en=province_en, parent=areadealer, sf_parent=areadealer, level=5)
        #城市
        citydealer, create = create_dealer(city_cn, city_cn, city_cn, True, None, name_en=city_en, province_cn=province_cn, province_en=province_en, city_cn=city_cn, city_en=city_en, parent=areadealer, sf_parent=provincedealer, level=2)
#        #集团
        jtdealer = None
#        if jt_code:
#            jtdealer, create = create_dealer(jt_code, jt_name_cn, jt_name_cn, True, dt, name_en=jt_name_en, parent=dealer_nation, jt_parent=dealer_nation, level=6)
        #小区
        xqdealer = None
        if xq_code:
            xqdealer, create = create_dealer(xq_code, xq_name_cn, xq_name_cn, True, None, parent=dealer_nation,jt_parent=jtdealer, xq_parent=areadealer, level=4)
            _add_user(xq_code, xq_code, '123456', [AREA_GROUP], [SHOW_ALL_PAGE], xqdealer)
        #经销商
        d, create = create_dealer(dealer_code, name_cn, abbr_cn, False, dt, name_en=name_en, abbr_en=abbr_en, province_cn=province_cn, province_en=province_en, city_cn=city_cn, city_en=city_en, new_old=new_old, parent=citydealer, jt_parent=None, xq_parent=xqdealer, sf_parent=citydealer, dt_parent=dealer_dt, level=3)
        term.dealers.add(d)
        if create:
            if dealer_code in ['35649','36422','36557','36868','37032']:
                _add_user('%s_M'%dealer_code, '%s_M'%dealer_code, '%s_M'%dealer_code, [DEALER_GROUP], [SHOW_ALL_PAGE], d)
            else:
                _add_user(dealer_code, dealer_code, dealer_code, [DEALER_GROUP], [SHOW_ALL_PAGE], d)
            
def create_dealer(code, name_cn, abbr_cn, has_child, dealertype, name_en=None, abbr_en=None, province_cn=None, province_en=None, city_cn=None, city_en=None, address=None, tel=None, new_old=None, parent=None, jt_parent=None, xq_parent=None, sf_parent=None, dt_parent=None, termid=None, level=None):        
    dealer, create = Dealer.objects.get_or_create(name=code, dealertype=dealertype, has_child=has_child, level=level)

    dealer.name_cn = name_cn
    dealer.name_en = name_en
    dealer.abbr_cn = abbr_cn
    dealer.abbr_en = abbr_en
    dealer.city_cn = city_cn
    dealer.city_en = city_en
    dealer.province_cn = province_cn
    dealer.province_en = province_en
    dealer.address = address
    dealer.tel = tel
    dealer.parent = parent
    dealer.jt_parent = jt_parent
    dealer.xq_parent = xq_parent
    dealer.sf_parent = sf_parent
    dealer.dt_parent = dt_parent
    dealer.termid = termid
    dealer.level = level
    dealer.new_old = new_old
    
    dealer.save()
    return dealer, create

def init_dealer():
    dt_bmw = add_dealertype('BMW')
    dt_mini = add_dealertype('MINI')
    
    dealer_nation = Dealer.objects.get_or_create(name=u'全国', name_cn=u'全国', name_en='Nation', abbr_cn=u'全国', has_child=True, level=0)[0]
    user = User.objects.get(id=1)
    up = UserProfile.objects.get_or_create(user=user)[0]
    up.dealer = dealer_nation
    up.save()
    
    dealer_bmw = Dealer.objects.get_or_create(name=u'BMW', name_cn=u'BMW', name_en='BMW', abbr_cn=u'BMW', has_child=True, parent=dealer_nation, dt_parent=dealer_nation, level=7)[0]
    dealer_mini = Dealer.objects.get_or_create(name=u'MINI', name_cn=u'MINI', name_en='MINI', abbr_cn=u'MINI', has_child=True, parent=dealer_nation, dt_parent=dealer_nation, level=7)[0]
    
    xlsfile = os.path.join(settings.SITE_ROOT, 'doc', 'dealer', u'APQ Dealer List for Q1 2014-0321区域权限更新.xls')
    book = xlrd.open_workbook(xlsfile)
    
    term = get_cur_input_term()
    term.dealers = []
    
    sh = book.sheet_by_index(0)
    print 'init dealer for bmw ...'
    save_dealer_bmw(sh, dealer_nation, dealer_bmw, dt_bmw, term)
    print 'ok'
    sh = book.sheet_by_index(1)
    print 'init dealer for mini ...'
    save_dealer_mini(sh, dealer_nation, dealer_mini, dt_mini, term)
    print 'ok'
    
    term.save()

if __name__ == '__main__':
    init_dealer()
    
