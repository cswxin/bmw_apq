#encoding:utf-8
import os, sys

sys.path.insert(0, os.path.abspath(os.curdir))
from service.easyExcel import easyExcel
from releaseinfo import REL_SITE_ROOT
DOC_ROOT = os.path.join(REL_SITE_ROOT, 'doc')
from mc.models import Dealer, DealerType

def add_dealertype(name):
    dt = DealerType.objects.get_or_create(name_cn=name)[0]
    dt.name_en = name
    dt.save()
    return dt

def count_dealer(sheet_index):
    dt_bmw = add_dealertype('BMW')
    dt_mini = add_dealertype('MINI')
    
    file_name = u'系统权限明细 Q3 2014 账户&密码 -20140918.xlsx'
    xls_file = os.path.join(DOC_ROOT, file_name)
    print xls_file
    excel = easyExcel(xls_file)
    
    try:
        
        for row in range(4, 58):
            name = excel.getRangeVal(sheet_index, 'C%s' % row)
            if not name:
                continue
            if isinstance(name, (int, float)):
                xq_name = int(name)
                xq_dealer_list = Dealer.objects.filter(name=xq_name)
                if xq_dealer_list:
                    xq_dealer = xq_dealer_list[0]
                    bmw_count = Dealer.objects.filter(xq_parent=xq_dealer, dealertype=dt_bmw, has_child=False).count()
                    mini_count = Dealer.objects.filter(xq_parent=xq_dealer, dealertype=dt_mini, has_child=False).count()
                    count = Dealer.objects.filter(xq_parent=xq_dealer, has_child=False).count()
                    excel.setRangeValBySheetIndex(sheet_index, 'H%s' % row, bmw_count)
                    excel.setRangeValBySheetIndex(sheet_index, 'I%s' % row, mini_count)
                    excel.setRangeValBySheetIndex(sheet_index, 'J%s' % row, count)
                else:
                    excel.setRangeValBySheetIndex(sheet_index, 'H%s' % row, 0)
                    excel.setRangeValBySheetIndex(sheet_index, 'I%s' % row, 0)
                    excel.setRangeValBySheetIndex(sheet_index, 'J%s' % row, 0)
                  
            else:
                if name == 'North':
                    name_cn = u'北区'
                if name == 'South':
                    name_cn = u'南区'
                if name == 'East':
                    name_cn = u'东区'
                if name == 'West':
                    name_cn = u'西区'
                if name == 'SouthEast':
                    name_cn = u'东南区'
                region_dealer = Dealer.objects.get(name_cn=name_cn)
                bmw_count = Dealer.objects.filter(xq_parent__xq_parent=region_dealer, dealertype=dt_bmw, has_child=False).count()
                mini_count = Dealer.objects.filter(xq_parent__xq_parent=region_dealer, dealertype=dt_mini, has_child=False).count()
                count = Dealer.objects.filter(xq_parent__xq_parent=region_dealer, has_child=False).count()
                excel.setRangeValBySheetIndex(sheet_index, 'H%s' % row, bmw_count)
                excel.setRangeValBySheetIndex(sheet_index, 'I%s' % row, mini_count)
                excel.setRangeValBySheetIndex(sheet_index, 'J%s' % row, count)
                
                
                
    finally:
        excel.save()
        excel.close()
    
if __name__ == "__main__":
    sheet_index = 2
    count_dealer(sheet_index)
    
