#encoding:utf-8
import os,sys
from mc.models import Province,City
from django.db.transaction import commit_on_success

province_dict = {}

@commit_on_success
def add_city():
    script_path = os.path.dirname(os.path.abspath(__file__))
    City.objects.all().delete()
    Province.objects.all().delete()
    
    for line in file('%s/city_province.txt' % script_path).read().split('\n'):
        if not line:
            continue
        city_name,province_name = line.split('\t')
        province = province_dict.get(province_name)
        if not province:
            province,is_create = Province.objects.get_or_create(name=province_name)
            if is_create:
                province.save()
            province_dict[province_name] = province
        city,create = City.objects.get_or_create(name=city_name,province=province)

if __name__ == '__main__':
    add_city()
