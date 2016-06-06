#encoding:utf-8
import os, sys
sys.path.insert(0, os.path.abspath(os.curdir))
from mc.models import Dealer

'''
修复以前竞品城市，省份 无英文问题 
'''
def fixCityProvinceEnName():
    dealers = Dealer.objects.filter(id__gt=1)
    cndict = {}
    for d in dealers:
        if d.city_cn is not None:
            city_en = cndict.get(d.city_cn, None)
            if city_en is None and d.city_en:
                cndict[d.city_cn] = d.city_en
        if d.province_cn is not None:
            province_en = cndict.get(d.province_cn, None)
            if province_en is None and d.province_en:
                cndict[d.province_cn] = d.province_en
    for d in dealers:
        makred = False
        if d.city_en is None and d.city_cn:
            d.city_en = cndict[d.city_cn]
            makred = True
        if d.province_en is None and d.province_cn:
            d.province_en = cndict[d.province_cn]
            makred = True
        if makred:
            print 'fix: ', d.id
            d.save()
            
if __name__ == '__main__':
    fixCityProvinceEnName()
    
