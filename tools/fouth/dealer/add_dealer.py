#encoding:utf-8

import os, sys
sys.path.insert(0, os.path.abspath(os.curdir))

from django.db.transaction import commit_on_success
from mc.models import Dealer, DealerType, City, Province
from mc import get_cur_input_term
from django.contrib.auth.models import User, Group
from userpro.models import UserProfile, UserPermission
from userpro.enums import *
import constant
import xlrd
from utils.xpinyin import Pinyin
pinyin = Pinyin()

from django.conf import settings

LISTORDER = 1
@commit_on_success
def update_dealer_listorder(parent=None):
    global LISTORDER
    if not parent:
        LISTORDER = 1
        parent = Dealer.objects.get(pk=1)
        parent.listorder = LISTORDER
        parent.save()
    sub_dealer_list = Dealer.objects.filter(parent=parent).order_by('id')
    for sub_dealer in sub_dealer_list:
        LISTORDER += 1
        sub_dealer.listorder = LISTORDER
        sub_dealer.save()
        if sub_dealer.has_child:
            update_dealer_listorder(sub_dealer)

dealer_dict = {}
sf_dict = {}
cs_dict = {}

def _float_to_str(text):
    if isinstance(text, float):
        return '%s' % int(text)
    else:
        return text.strip()

def add_row(sh, rx, dealer_nation, dealertype_bmw, term):
        texts = sh.row_values(rx)
        #print texts
        
        dealer_code = _float_to_str(texts[0])
        dealer_abbr_cn = texts[1].strip()
        dealer_name = texts[2].strip().split('\n')
        dealer_name_en = dealer_name[0].strip()
        dealer_name_cn = dealer_name[1].strip()
        city = texts[3].strip().split('\n')
        city_en = city[0].strip()
        city_cn = city[1].strip()
        province = texts[4].strip().split('\n')
        province_en = province[0].strip()
        province_cn = province[1].strip()
        regions = texts[5].strip().split('\n')
        region1_name = regions[0].strip() #大区的name
        region1_name_cn = regions[1].strip() #大区的name
        region2_name = city_cn #参照以前老层级关系城市的name
        
        #大区
        daqu_dealer = dealer_dict.get(region1_name)
        if region1_name != '':
            if not daqu_dealer:
                #print 'level-1', region1_name
                daqu_dealer, create = Dealer.objects.get_or_create(name=region1_name, level=constant.LEVEL_DAQU)
                daqu_dealer.name_cn = region1_name_cn
                daqu_dealer.name_en = region1_name
                daqu_dealer.has_child = True
                daqu_dealer.save()
                dealer_dict[daqu_dealer.name] = daqu_dealer
            
            if dealer_nation:
                daqu_dealer.parent = dealer_nation
                daqu_dealer.sf_parent = dealer_nation
                daqu_dealer.xq_parent = dealer_nation
                daqu_dealer.save()
            
        #经销商集�
        jt_dealer_name_en = texts[6].strip()
        jt_dealer_name_cn = texts[7].strip()
        jt_dealer_code = _float_to_str(texts[8])
        
        jt_dealer = dealer_dict.get(jt_dealer_code)
        if jt_dealer_code != '':
            if not jt_dealer:
                #print 'jt_dealer', jt_dealer_code
                jt_dealer, create = Dealer.objects.get_or_create(name=jt_dealer_code, level=constant.LEVEL_JT)
                jt_dealer.name_cn = jt_dealer_name_cn
                jt_dealer.name_en = jt_dealer_name_en
                jt_dealer.parent = dealer_nation
                jt_dealer.jt_parent = dealer_nation
                jt_dealer.has_child = True
                jt_dealer.save()
                dealer_dict[jt_dealer.name] = jt_dealer
        
        #小区
        xq_dealer_name_en = texts[9].strip()
        xq_dealer_name_cn = texts[9].strip()
        xq_dealer_code = _float_to_str(texts[10])
        new_dealer = texts[11].strip()
        xq_dealer = dealer_dict.get(xq_dealer_code)
        if xq_dealer_code != '':
            if not xq_dealer:
                #print 'xq_dealer', xq_dealer_code
                xq_dealer, create = Dealer.objects.get_or_create(name=xq_dealer_code, level=constant.LEVEL_XQ)
                xq_dealer.name_cn = xq_dealer_name_cn
                xq_dealer.name_en = xq_dealer_name_en
                xq_dealer.parent = dealer_nation
                xq_dealer.has_child = True
                xq_dealer.save()
                save_dealer_user(xq_dealer_code, xq_dealer_name_en, DEALER_GROUP, xq_dealer, False)
                dealer_dict[xq_dealer.name] = xq_dealer
        
            if daqu_dealer:
                xq_dealer.xq_parent = daqu_dealer
                xq_dealer.save()
        
        #省份
        sf_dealer_name_en = province_en
        sf_dealer_name_cn = province_cn
        sf_dealer_code = province_cn
        
        sf_dealer = sf_dict.get(sf_dealer_code)
        if sf_dealer_code != '':
            if not sf_dealer:
                #print 'sf_dealer', sf_dealer_code
                sf_dealer, create = Dealer.objects.get_or_create(name=sf_dealer_code, level=constant.LEVEL_PROVINCE)
                sf_dealer.name_cn = sf_dealer_name_cn
                sf_dealer.name_en = sf_dealer_name_en
                sf_dealer.has_child = True
                sf_dealer.save()
                sf_dict[sf_dealer.name] = sf_dealer
                
            if daqu_dealer:
                sf_dealer.parent = daqu_dealer
                sf_dealer.sf_parent = daqu_dealer
                sf_dealer.save()
            
        need_create = False
        city_dealer = cs_dict.get(region2_name)
        if region2_name != '':
            if not city_dealer:
                #print 'level-2', region2_name
                city_dealer, create = Dealer.objects.get_or_create(name=region2_name, level=constant.LEVEL_CITY)
                city_dealer.name_cn = region2_name
                city_dealer.name_en = city_en
                city_dealer.parent = daqu_dealer
                city_dealer.sf_parent = Dealer.objects.get(name=sf_dealer_code, level=constant.LEVEL_PROVINCE)
                if region2_name == sf_dealer_code:
                    print Dealer.objects.get(name=sf_dealer_code, level=constant.LEVEL_PROVINCE).id
                city_dealer.has_child = True
                city_dealer.save()
                cs_dict[city_dealer.name] = city_dealer
            
        leaf_dealer = dealer_dict.get(dealer_code)
        #print 'dealer', dealer_code
        leaf_dealer, create = Dealer.objects.get_or_create(name=dealer_code)
        leaf_dealer.name_cn = dealer_name_cn
        leaf_dealer.name_en = dealer_name_en
        leaf_dealer.parent = city_dealer
        if dealertype_bmw.name_en == 'MINI': 
            leaf_dealer.jt_parent = jt_dealer
            leaf_dealer.xq_parent = xq_dealer
            leaf_dealer.sf_parent = city_dealer
        else:
            if jt_dealer:
                leaf_dealer.jt_parent = jt_dealer
            if xq_dealer:
                leaf_dealer.xq_parent = xq_dealer
            if city_dealer:
                leaf_dealer.sf_parent = city_dealer
        leaf_dealer.has_child = False
        leaf_dealer.abbr_cn = dealer_abbr_cn
        leaf_dealer.dealertype = dealertype_bmw
        leaf_dealer.city_cn = city_cn
        leaf_dealer.city_en = city_en
        leaf_dealer.province_cn = province_cn
        leaf_dealer.province_en = province_en
        if new_dealer is not None and new_dealer == 'Y':
            leaf_dealer.termid = term.id
#        else:
#            leaf_dealer.termid = None
#            if dealertype_bmw.name_en == 'BMW':
#                leaf_dealer.termid = 4
        leaf_dealer.level = constant.LEVEL_DEALER
        if str(dealer_code).endswith('_M'):
            bmw_cd = dealer_code[0:-2]
            dealer_code = bmw_cd
            try:
                leaf_dealer.email = Dealer.objects.get(name=bmw_cd).email
            except Exception, ex:
                print bmw_cd, 'not existed'
        leaf_dealer.save()
        term.dealers.add(leaf_dealer)
        save_dealer_user(dealer_code, dealer_abbr_cn, DEALER_GROUP, leaf_dealer, False)
        dealer_dict[leaf_dealer.name] = leaf_dealer
        
@commit_on_success
def add_dealer():
    dealertype_bmw = DealerType.objects.get(name_en=u'BMW')
    dealer_nation = Dealer.objects.get(name=u'全国')
    
    xlsfile = os.path.join(settings.RESOURCES_ROOT, u'first/dealer/APQ 2012 dealer list _0220.xls')
    book = xlrd.open_workbook(xlsfile)
    
    #经销�
    sh = book.sheet_by_index(0)
    print sh.name, sh.nrows, sh.ncols
    term = get_cur_input_term()
    term.dealers = []
    for rx in range(1, sh.nrows):
        add_row(sh, rx, dealer_nation, dealertype_bmw, term)
        #break
    term.save()

@commit_on_success
def add_dealer_2():
    dealertype_bmw = DealerType.objects.get(name_en=u'BMW')
    dealer_nation = Dealer.objects.get(name=u'全国')
    
#    xlsfile = os.path.join(settings.RESOURCES_ROOT, u'third/dealer/APQ 2012 dealer list _To GFK_0723.xls')
#    xlsfile = os.path.join(settings.RESOURCES_ROOT, u'third/dealer/APQ 2012 dealer list _To GFK_0829.xls')
#    xlsfile = os.path.join(settings.RESOURCES_ROOT, u'third/dealer/APQ 2012 dealer list _To GFK_0918.xls')
    xlsfile = os.path.join(settings.RESOURCES_ROOT, u'fouth/dealer/BMW Q4经销商大区经理小区经理调整_1214.xls')
    
    book = xlrd.open_workbook(xlsfile)
    
    term = get_cur_input_term()
    #BMW经销
    sh = book.sheet_by_index(0)
    print sh.name, sh.nrows, sh.ncols
    term.dealers = []
    for rx in range(1, sh.nrows):
        add_row(sh, rx, dealer_nation, dealertype_bmw, term)
        #break
    
    #MINI经销
    dealertype_mini = DealerType.objects.get(name_en=u'MINI')
    sh = book.sheet_by_index(1)
    print sh.name, sh.nrows, sh.ncols
    for rx in range(1, sh.nrows):
        add_row(sh, rx, dealer_nation, dealertype_mini, term)
    term.save()

#后台：没有登录后台的权限。
#前台：只可以看到经销商自己的“单店报告”和自己的“历史\现在\未来数据”。
def save_dealer_user(username, firstname, groupname, dealer, is_staff, is_active=True):
    name = pinyin.get_pinyin(username)
    u, created = User.objects.get_or_create(username=name)
    if not created:
        return
    u.first_name = firstname
    u.set_password('191919')
    u.is_staff = is_staff
    u.is_active = is_active
    g = Group.objects.get(name=groupname)
    u.groups = [g, ]
    
    up, create = UserProfile.objects.get_or_create(user=u)
    per, create = UserPermission.objects.get_or_create(name=SHOW_DEALER_PAGE)
    up.user_permissions = [per, ]
    up.dealer = dealer #可见的经销商
    up.save()
    u.save()
    print  u.username, 'created'

@commit_on_success
def add_mini_dealertype():
    dt, create = DealerType.objects.get_or_create(name_cn='MINI')
    dt.name_en = 'MINI'
    dt.save()
    
def add_MINI_dealer():
    dealertype_mini = DealerType.objects.get(name_en=u'MINI')
    dealer_nation = Dealer.objects.get(name=u'全国')
    
    xlsfile = os.path.join(settings.RESOURCES_ROOT, u'first/dealer/Mini经销商名单_0415.xls')
    book = xlrd.open_workbook(xlsfile)
    
    #经销�
    sh = book.sheet_by_index(0)
    print sh.name, sh.nrows, sh.ncols
    term = get_cur_input_term()
    for rx in range(1, sh.nrows):
        add_row(sh, rx, dealer_nation, dealertype_mini, term)
        #break
    term.save()

def update_dealer_mail():
     xlsfile = os.path.join(settings.RESOURCES_ROOT, u'first/dealer/APQ Dealer_Email ID List_0316.xls')
     book = xlrd.open_workbook(xlsfile)
     lists = []
     sh = book.sheet_by_index(0)
     __update_sheet(sh, lists)
     sh = book.sheet_by_index(1)
     __update_sheet(sh, lists)
     sh = book.sheet_by_index(2)
     __update_sheet(sh, lists)
     sh = book.sheet_by_index(3)
     __update_sheet(sh, lists)
     print len(lists), len(set(lists))
def __update_sheet(sh, lists):
    for rx in range(1, sh.nrows):
        texts = sh.row_values(rx)
        #print texts
        dealer_code = _float_to_str(texts[0])
        email = str(texts[5]).strip()
        dealer = Dealer.objects.get(name=dealer_code)
        lists.append(dealer_code)
        dealer.email = email
        dealer.save()
        
        
def add_dealers():
    add_mini_dealertype()
#    add_dealer()
    add_dealer_2()
    #update_dealer_mail()
    #add_MINI_dealer()
    update_dealer_listorder()
    
    
    
if __name__ == '__main__':
    add_dealers()
    
