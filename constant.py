#encoding:utf-8
'''
常量�
'''
old_project_id = 1
current_project_id = 2 #当前BMW project
current_mini_project_id = 3 #当前MINI
competition_project_id = 4 #当前竞品

BRAND_BMW = 1

LEVEL_NATION = 0    #全国
LEVEL_DAQU = 1      #大区
LEVEL_CITY = 2      #城市
LEVEL_DEALER = 3    #经销�
LEVEL_XQ = 4        #小区
LEVEL_PROVINCE = 5  #省份
LEVEL_JT = 6        #经销商集�
LEVEL_BRAND = 7 #品牌
maximun = 80 #SQL in 中数据的拆分长度 
def dealertype_id_to_project_id(dealer_type_id):
    ''' BMW: dealer_type_id = 1, project_id = 2
        MINI: dealer_type_id = 2, project_id =2
        others:  project_id = 0
    '''
    project_id = 0
    if dealer_type_id == 1:
        project_id = 1
    elif dealer_type_id == 2:
        project_id = 2
#    else:
#        project_id = 3
    return project_id

#数据对比归类
data_compare_regional_name = 'regional'
data_compare_province_name = 'province'
data_compare_city_name = 'city'
data_compare_subdistrict_name = 'subdistrict'
data_compare_dealergroup_name = 'group'
data_compare_brand_name = 'brand'
data_compare_user_name = 'user'
data_compare_num_name = 'num'
data_compare_newold_name = 'newold'
data_compare_dict = {
    data_compare_regional_name:u'大区',
    data_compare_province_name: u'省份',
    data_compare_city_name: u'城市',
    data_compare_subdistrict_name: u'小区',
    data_compare_dealergroup_name: u'经销商集团',
    data_compare_brand_name: u'品牌',
    data_compare_user_name:u'评估员',
    data_compare_num_name:u'进店人数',
    data_compare_newold_name:u'新店和老店',
}
data_compare_en_dict = {
    data_compare_regional_name:'Region',
    data_compare_province_name: 'Province',
    data_compare_city_name: 'City',
    data_compare_subdistrict_name: 'Sub district',
    data_compare_dealergroup_name: 'Dealer Group',
    data_compare_brand_name:'Brand',
    data_compare_user_name:'Auditor',
    data_compare_num_name:'No. of visitor',
    data_compare_newold_name:'Old & new dealer',
}

data_compare_kind_dict = {
    data_compare_regional_name:LEVEL_DAQU,
    data_compare_province_name:LEVEL_PROVINCE,
    data_compare_city_name:LEVEL_CITY,
    data_compare_subdistrict_name:LEVEL_XQ,
    data_compare_dealergroup_name:LEVEL_JT,
    data_compare_brand_name: LEVEL_BRAND,
}

#按期次确定的新店老店
new_old_dict = {5:['34016', '35009', '35410', '35617', '35765', '35815', '35817', '35876', '35922', '35923', '36099', '36159', '36338'],
                6:['34016', '35009', '35410', '35617', '35765', '35815', '35817', '35876', '35922', '35923', '36099', '36159', '36338']}
