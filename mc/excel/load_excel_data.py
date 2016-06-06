#encoding:utf-8

import os, sys
sys.path.insert(0, os.path.abspath(os.curdir))

from django.db.transaction import commit_on_success
from mc.models import Dealer, Paper, Term, Report
from survey.models import Respondent

from django.contrib.auth.models import User

from django.conf import settings
import time, os, sys, shutil
from django.db import connection
from django.db.utils import DatabaseError
import xlrd

QUESTION_START = ('A', 'B', 'C', 'D', 'E', 'F')

def _get_xiaoshou_filed(name):
    name = name.replace('(', '')
    name = name.replace(')', '')
    
    return name

def get_file_data(filename):
    filename = filename.replace('/', '\\')
    book = xlrd.open_workbook(filename)
    sh = book.sheet_by_index(0)
    return sh
    
@commit_on_success
def add_third_data():
    xlsfile = os.path.join(settings.SITE_ROOT, u'doc/from_customer/Q3_最终数据_1021.xls')
    sh = get_file_data(xlsfile)
    
    firstline = sh.row_values(2)
    numdict, indexes = _get_num_dict(firstline)
    
    print numdict
    print indexes
    
    for rx in range(3, sh.nrows):
        fields = sh.row_values(rx)
        _update_one_question(fields, indexes, numdict)

def _get_num_dict(firstline):
    fields = firstline
    numdict = {}
    i = 0
    indexes = []
    for f in fields:
        f = f.strip()
        if len(f) < 4 and _is_question_field(f):
            f = _get_xiaoshou_filed(f)
            numdict[i] = f
            indexes.append(i)
        
        i += 1
    
    numdict[8] = 'total'
    indexes.append(8)
    
    numdict[11] = 'A'
    indexes.append(11)
    
    numdict[21] = 'B'
    indexes.append(21)
    
    numdict[46] = 'C'
    indexes.append(46)
    
    numdict[59] = 'D'
    indexes.append(59)
    
    return numdict, indexes

#判断是否为问题的开始字段
def _is_question_field(name):
    for s in QUESTION_START:
        if name.startswith(s):
            return True
    
    return False

#判断是否为空
def _isempty(fields, indexes):
    maxf = 2
    count = 0
    for i in indexes:
        f = fields[i].strip()
        if f:
            count += 1
            if count > maxf:
                return False
    
    return True

#更新第三期的一条记录
def _update_one_question(fields, indexes, numdict):
    f = fields[1]
    if hasattr(f, 'strip'):        
        dealer_sn = f.strip()
    else:
        dealer_sn = str(int(f))
    
    if not dealer_sn:
        areaname = fields[4].strip()
        if areaname == u'National':
            areaname = u'全国'
        dealer = _get_dealer(areaname)
    else:
        dealer = _get_dealer(dealer_sn)
    
    #print dealer_sn
    
    if not dealer:
        return
    
    #if _isempty(fields,indexes):
    #    return
    
    rs = Report.objects.filter(term__id=3, dealer=dealer)
    for r in rs:
        fs = []
        sql = u'update mc_reportdata set '
        for i in indexes:
            name = fields[i]
            if hasattr(name, 'strip'):
                name = name.strip()
            
            if name == u'不适用':
                f = u'%s=null' % numdict[i]
            else:
                f = u'%s=\'%s\'' % (numdict[i], name)
            
            fs.append(f)
        
        sql += ','.join(fs)
        sql += u' where id=%d' % r.id
        
        #print sql
        try:
            import DbUtils
            try:
                c, con = DbUtils.cursor()
                c.execute(sql)
                if con:
                    con.commit()
            finally:
                if c:
                    c.close()
                if con:
                    con.close()   
        except DatabaseError, e:
            print e
            print sql
        
        total = fields[8]
        r.score = total
        r.save()
        
        ps = Paper.objects.filter(dealer=dealer, term__id=3)
        for p in ps:
            p.score = total
            p.save()        
    
def _get_dealer(dealername):
    dealername = dealername.strip()
    try:
        dealer = Dealer.objects.get(name=dealername)
    except Dealer.DoesNotExist:
        print u'不存在的 %s' % dealername
        return None
    
    return dealer

import win32com.client as win32

def _open_excel_file(xls_file):
    xl = win32.gencache.EnsureDispatch('Excel.Application')
    xl.Visible = False
    xl.DisplayAlerts = False
    
    #xls_file = xls_file.replace('/','\\')
    
    ss = xl.Workbooks.Open(xls_file) #必须是绝对路径
    ss.Visible = False
    return ss
    
if __name__ == '__main__':    
    add_third_data()    
    
