#encoding:utf-8
from mc.models import DealerType, Dealer, Paper, Term
from mc import enums, utils 
from mcview.decorator import cached 
from django.contrib.auth.models import Group
import constant

def get_dealer_by_username(username):
    try:
        dealer = Dealer.objects.get(name=username)
        return dealer
    except:
        return None

@cached('dealer_type')
def get_dealer_types():
    '''经销商类型查询接口，返回值为所有经销商的queryset'''
    return DealerType.objects.all().order_by('id')

def get_dealer_count_by_dealertype(dealertype, term):
    cache_key = 'dealer_count_by_dealertype_%s_%s' % (term.id, dealertype.id)
    
    @cached(cache_key)
    def _inner():
        if dealertype.name_en == 'BMW':
            dealer_count = term.dealers.filter(dealertype=dealertype).count()
        else:
            dealer_count = term.dealers.filter(dealertype=dealertype).count()
#            dealer_count = Dealer.objects.filter(dealertype=dealertype).count()
#        else:
#            dealer_count = 15 #不管竞品对应的经销商有多少,只取15家
        return dealer_count
    return _inner()

def get_dealertype_done_survey_count(dealertype, term):
    '''按经销商类型汇总的完成数查询接口'''
    paper_type = enums.BMW_PAPER_TYPE
#    if dealertype.name_en == 'BMW' or dealertype.name_en == 'MINI':
#        paper_type = enums.BMW_PAPER_TYPE
#    else:
    paper_type = enums.FW_PAPER_TYPE
    return Paper.objects.filter(paper_type=paper_type, term=term, status__gte=enums.FW_PAPER_STATUS_WAIT_AUDIT_1, dealer__dealertype=dealertype).count()
        

ROOT_DEALER = None
def get_root_dealer():
    global ROOT_DEALER
    if ROOT_DEALER is None:
        ROOT_DEALER = Dealer.objects.filter(parent=None).order_by('listorder', 'id')[:1][0]
    return ROOT_DEALER

DEALERTYPE_BMW = None
def get_dealertype_BMW():
    global DEALERTYPE_BMW
    if DEALERTYPE_BMW is None:
        DEALERTYPE_BMW = DealerType.objects.get(name_en='BMW')
    return DEALERTYPE_BMW

def get_regionals():
    '''区域查询接口，返回值为4大区域的queryset'''
    return Dealer.objects.filter(xq_parent=get_root_dealer())

def get_dealer_count_by_region(region, term):
    cache_key = 'dealer_count_by_region_%s' % region.id
    @cached(cache_key)
    def _inner():
        all_dealer_id_list = utils.get_sub_leaf_dealer_id_list(region)
        all_dealer_id_list = [d.id for d in term.dealers.filter(id__in=all_dealer_id_list)]
        all_bmw_dealer_id_list = [dealer['id'] for dealer in Dealer.objects.filter(dealertype=get_dealertype_BMW(), has_child=False).values('id')]
        id_set = set(all_dealer_id_list) & set(all_bmw_dealer_id_list)
        dealer_count = len(id_set)
        return dealer_count
    return _inner()

def get_regional_done_survey_count(region, term):
    '''按区域汇总的完成数查询接口'''
    sub_dealer_id_list = utils.get_sub_leaf_dealer_id_list(region)
    sub_dealer_id_list = [d.id for d in term.dealers.filter(id__in=sub_dealer_id_list)]
    all_bmw_dealer_id_list = [dealer['id'] for dealer in Dealer.objects.filter(dealertype=get_dealertype_BMW(), has_child=False).values('id')]
    sub_dealer_id_set = set(sub_dealer_id_list) & set(all_bmw_dealer_id_list)
    
    dealer_id_list = [paper['dealer_id'] for paper in Paper.objects.filter(paper_type=enums.FW_PAPER_TYPE, term=term, status__gte=enums.FW_PAPER_STATUS_WAIT_AUDIT_1, dealer__id__in=sub_dealer_id_set).values('dealer_id')]
    return len(set(dealer_id_list))

def get_paper_list_by_term(term):
    paper_list = Paper.objects.filter(term=term)
    return paper_list


def get_leaf_dealer_id_for_bm(term, region=None):
    return [d.id for d in get_leaf_dealer_for_bm(term, region)]

@cached('bmw_dealer_list')
def get_leaf_dealer_for_bm(term, region=None):
    dealertype_bm = DealerType.objects.get(name_en='BMW')
    if not region:
        return term.dealers.filter(has_child=False, dealertype=dealertype_bm).order_by('listorder', 'id')
    else:
        sub_dealer_id_list = utils.get_sub_leaf_dealer_id_list(region)
        sub_dealer_id_list = [d.id for d in term.dealers.filter(id__in=sub_dealer_id_list)]
        return Dealer.objects.filter(has_child=False, dealertype=dealertype_bm, id__in=sub_dealer_id_list).order_by('listorder', 'id').exclude(termid='')
@cached('mini_dealer_list')
def get_leaf_dealer_for_mini(term, region=None):
    dealertype_bm = DealerType.objects.get(name_en='MINI')
    if not region:
        return term.dealers.filter(has_child=False, dealertype=dealertype_bm).order_by('listorder', 'id')
    else:
        sub_dealer_id_list = utils.get_sub_leaf_dealer_id_list(region)
        sub_dealer_id_list = [d.id for d in term.dealers.filter(id__in=sub_dealer_id_list)]
        return Dealer.objects.filter(has_child=False, dealertype=dealertype_bm, id__in=sub_dealer_id_list).order_by('listorder', 'id')

@cached('others_dealer_list')
def get_leaf_dealer_other_than_bm(term, region=None):
    dealertype_list = DealerType.objects.exclude(name_en__in=['BMW', 'MINI'])
    if not region:
        return Dealer.objects.filter(has_child=False, dealertype__in=dealertype_list).order_by('dealertype__name_en', 'listorder')
    else:
        sub_dealer_id_list = utils.get_sub_leaf_dealer_id_list(region)
        #sub_dealer_id_list = [d.id for d in term.dealers.filter(id__in=sub_dealer_id_list)]
        return Dealer.objects.filter(has_child=False, dealertype__in=dealertype_list, id__in=sub_dealer_id_list).order_by('dealertype__name_en', 'listorder')

# 封装递归函数
def get_sub_leaf_dealer_list(dealer, refresh=False):
    @cached('sub_leaf_dealer_list_%d' % dealer.id)
    def __inner(refresh=False):
        sub_list = []
        get_sub_leaf_dealer_list1(dealer, sub_list)
        return set(sub_list)
    return __inner(refresh=refresh)

# 递归函数
def get_sub_leaf_dealer_list1(dealer, sub_list):
    """得到所有子叶子节点列表"""
    if dealer.has_child:
        if dealer.level <= 2: #老版本
            for child in Dealer.objects.filter(parent=dealer).order_by('listorder'):
                get_sub_leaf_dealer_list1(child, sub_list)
        elif dealer.level == 3:#经销商节点
            pass
        elif  dealer.level == 4:#按小区
            for child in Dealer.objects.filter(xq_parent=dealer).order_by('listorder'):
                get_sub_leaf_dealer_list1(child, sub_list)
        elif  dealer.level == 5:#按省份
            for child in Dealer.objects.filter(sf_parent=dealer).order_by('listorder'):
                get_sub_leaf_dealer_list1(child, sub_list)
        elif  dealer.level == 6:#按经销商集团
            for child in Dealer.objects.filter(jt_parent=dealer).order_by('listorder'):
                get_sub_leaf_dealer_list1(child, sub_list)
        elif  dealer.level == 7:#品牌
            for child in Dealer.objects.filter(dt_parent=dealer).order_by('listorder'):
                get_sub_leaf_dealer_list1(child, sub_list)
        pass
    else:
        sub_list.append(dealer)
        
def get_dealers_by_term_type(term, type_id):
    dealers = term.dealers.all().filter(dealertype__id=type_id)
    return dealers

def get_dealer_parent_by_level(dealer, level):
    if level <= constant.LEVEL_DEALER:
        while dealer.parent:
            if dealer.parent.level == level:
                return dealer.parent
            else:
                dealer = dealer.parent
    elif level == constant.LEVEL_XQ:
        while dealer.xq_parent:
            if dealer.xq_parent.level == level:
                return dealer.xq_parent
            else:
                dealer = dealer.xq_parent
    elif level == constant.LEVEL_PROVINCE:
        while dealer.sf_parent:
            if dealer.sf_parent.level == level:
                return dealer.sf_parent
            else:
                dealer = dealer.sf_parent
    elif level == constant.LEVEL_JT:
        while dealer.jt_parent:
            if dealer.jt_parent.level == level:
                return dealer.jt_parent
            else:
                dealer = dealer.jt_parent

def get_dealer(**kargs):
    try:
        return Dealer.objects.get(**kargs)
    except Dealer.DoesNotExist:
        return None
