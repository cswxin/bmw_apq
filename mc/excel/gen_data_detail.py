#encoding:utf-8

import os, sys, shutil
sys.path.insert(0, os.path.abspath(os.curdir))

from django.conf import settings

from mc.models import Term, Dealer
from mc import get_paper, enums

import xlwt
from django.db import connection
DEALER_REPORT_FOLDER = 'dealer_report'
import mc

NAME_DICT = {
'survey_code':u'问卷编号',
'consultant_name':u'访问员',
}

#生成数据大表
def gen_data_func(term,):    
    xls_file = _get_export_file(term.id)
    wbk = _open_excel_file(xls_file)
    
    fs = _get_field_list()
    
    try:
        dealer_list = Dealer.objects.filter(has_child=False)
        row1 = 1
        row2 = 1
        for dealer in dealer_list:
            print u'正在导出 %s' % dealer.name_cn
            
            data = _get_dealer_data(dealer, term, fs)
            if not data:
                continue
            
            dt = dealer.dealertype
            if dt.id == 1:
                sheet = wbk.get_sheet(0)
                row = row1
            else:
                sheet = wbk.get_sheet(1)
                row = row2
            
            _write_one_dealer(dealer, term, data, sheet, row)
            if dt.id == 1:
                row1 += 1
            else:
                row2 += 1
    finally:
        wbk.save(xls_file)

def _get_export_file(termid):
    reportpath = _get_report_path()
    filename = u'2011第%d期_问卷_信息.xls' % termid
    report_file = os.path.join(reportpath, filename)
    return report_file

def _get_report_path():
    reportpath = os.path.join(settings.MEDIA_ROOT, DEALER_REPORT_FOLDER)
    if not os.path.exists(reportpath):
        os.makedirs(reportpath)
    return reportpath

def _open_excel_file(xls_file):
    wbk = xlwt.Workbook()
    sheet1 = wbk.add_sheet(u'宝马问卷列表', cell_overwrite_ok=True)
    sheet2 = wbk.add_sheet(u'竞品问卷列表', cell_overwrite_ok=True)
    
    fields = _get_field_list()
    index = 0
    
    names_list = [u'期数', u'经销商名称', u'经销商地址', u'经销商编号']
    for f in names_list:
        sheet1.write(0, index, f)
        sheet2.write(0, index, f)
        index += 1
    
    for f in fields:
        f = NAME_DICT.get(f, f)
        sheet1.write(0, index, f)
        sheet2.write(0, index, f)
        index += 1
    
    return wbk

def _get_field_list():
    no_fs_list = ['term_id', 'dealer_code', 'appraiser_code', 'customer_code', 'id']
    sql = 'select * from survey_respondentdata;'
    import DbUtils
    try:
        c, con = DbUtils.cursor()
        c.execute(sql)
        con.commit()
        ret = c.fetchone()
        fields = []
        for i in c.description:
            f = i[0]
            if f not in no_fs_list:
                fields.append(f)
    finally:
        if c:
            c.close()
        if con:
            con.close()   
    return fields
    
#写一行数据
def _write_one_dealer(dealer, term, data, sheet, row):
    sheet.write(row, 0, u'第%d期' % term.id)
    sheet.write(row, 1, dealer.name_cn)
    sheet.write(row, 2, dealer.address)
    sheet.write(row, 3, dealer.name)
    
    index = 4
    for d in data:
        sheet.write(row, index, d)
        index += 1
    
#获得经销商的数据
def _get_dealer_data(dealer, term, fs):
    paper = mc.get_paper(dealer=dealer, term=term)
    if paper is None:
        return []
    
    resp = paper.respondent
    
    fs_str = ','.join(fs)
    sql = 'select %s from survey_respondentdata where id=%d;' % (fs_str, resp.id)
    import DbUtils
    try:
        c, con = DbUtils.cursor()
        c.execute(sql)
        con.commit()
        ret = c.fetchone()
    finally:
        if c:
            c.close()
        if con:
            con.close()   
    return ret

if __name__ == '__main__':
    if len(sys.argv) >= 2:
        termid = sys.argv[1]
        term = Term.objects.get(id=termid)
    else:
        term = mc.get_cur_term()
    
    gen_data_func(term)
