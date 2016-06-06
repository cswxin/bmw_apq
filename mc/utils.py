#encoding:utf-8
from mc.models import *
from django.db.transaction import commit_on_success
from django.db import connection
from django.core.cache import cache

# 封装递归函数
def get_parent_dealer_id_list(dealer):
    id_list = []
    if not dealer.parent:
        return [dealer.id]
    get_parent_dealer_id_list1(dealer, id_list)
    return id_list

# 递归函数
def get_parent_dealer_id_list1(dealer, id_list):
    if dealer.parent:
        get_parent_dealer_id_list1(dealer.parent, id_list)
    id_list.append(dealer.id)

# 封装递归函数
def get_sub_dealer_id_list(dealer):
    """得到所有子节点列表"""
    id_list = []
    get_sub_dealer_id_list1(dealer, id_list)
    return id_list

# 递归函数
def get_sub_dealer_id_list1(dealer, id_list):
    """得到所有子节点列表"""
    id_list.append(dealer.id)
    if dealer.has_child:
        for child in Dealer.objects.filter(parent=dealer).order_by('listorder'):
            get_sub_dealer_id_list1(child, id_list)

# 封装递归函数
def get_sub_dealer_id_list_without_leaf(dealer):
    """得到所有子节点列表"""
    id_list = []
    get_sub_dealer_id_list_without_leaf1(dealer, id_list)
    return id_list

# 递归函数
def get_sub_dealer_id_list_without_leaf1(dealer, id_list):
    """得到所有子节点列表"""
    if dealer.has_child:
        id_list.append(dealer.id)    
        for child in Dealer.objects.filter(parent=dealer).order_by('listorder'):
            get_sub_dealer_id_list_without_leaf1(child, id_list)

# 封装递归函数
def get_sub_leaf_dealer_id_list(dealer, refresh=False):
    cache_key = 'sub_leaf_dealer_id_list_%s' % dealer.id
    if refresh:
        id_list = None        
    else:
        id_list = cache.get(cache_key)
        
    if id_list is None:
        id_list = []
        get_sub_leaf_dealer_id_list1(dealer, id_list)
        cache.set(cache_key, id_list, 24 * 60 * 60)
    return id_list

# 递归函数
def get_sub_leaf_dealer_id_list1(dealer, id_list):
    """得到所有子叶子节点列表"""
    if dealer.has_child:
        for child in Dealer.objects.filter(parent=dealer).order_by('listorder'):
            get_sub_leaf_dealer_id_list1(child, id_list)
    else:
        id_list.append(dealer.id)

def get_dealer_tree():
    dealer = Dealer.objects.get(parent=None)
    get_dealer_tree1(dealer)
    return dealer

def get_dealer_tree1(dealer):
    if dealer.has_child:
        dealer.children = []
        for sub_dealer in Dealer.objects.filter(parent=dealer).order_by('listorder'):
            dealer.children.append(sub_dealer)
            get_dealer_tree1(sub_dealer)    

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

if __name__ == '__main__':
    pass
