#encoding:utf-8

import os, sys
sys.path.insert(0, os.path.abspath(os.curdir))

from django.db.transaction import commit_on_success
from mc.models import Dealer
import constant

from django.conf import settings

brand_dealer_dict = {}
@commit_on_success
def add_dealer():
    dealer_nation = Dealer.objects.get(name=u'全国')
    dealers = Dealer.objects.filter(level=constant.LEVEL_DEALER)
    if dealers:
        for dealer in dealers:
            brand_dealer = brand_dealer_dict.get(dealer.dealertype)
            if not brand_dealer:
                brand_dealer, create = Dealer.objects.get_or_create(name=dealer.dealertype.name_en, level=constant.LEVEL_BRAND)
                brand_dealer.name_cn = dealer.dealertype.name_cn
                brand_dealer.name_en = dealer.dealertype.name_en
                brand_dealer.parent = dealer_nation
                brand_dealer.dt_parent = dealer_nation
                brand_dealer.save()
                brand_dealer_dict[dealer.dealertype] = brand_dealer
            dealer.dt_parent = brand_dealer
            dealer.save()
    
if __name__ == '__main__':
    add_dealer()
    
