#encoding:utf-8

import os,sys
sys.path.insert(0,os.path.abspath(os.curdir))

from django.conf import settings
from mc.models import XlsReportHist,Dealer
from django.db.transaction import commit_on_success
import re
import time
import xlrd

HISTORY_PATH = os.path.join(settings.MEDIA_ROOT,'xls/2010')

@commit_on_success
def load_history():
    #XlsReportHist.objects.all().delete()
    
    fs = os.listdir(HISTORY_PATH)
    for f in fs:
        fullpath = os.path.join(HISTORY_PATH,f)
        print 'enter',fullpath
        if os.path.isdir(fullpath):
            names = f.split('_')
            termindex = int(names[1][1:])
            add_term_xsl(fullpath,termindex,f)

def add_term_xsl(fpath,termindex,fname):
    pat = ur'_([^_]*?)(\d+)_'
    fs = os.listdir(fpath)
    for f in fs:
        fullpath = os.path.join(fpath,f)
        #print fullpath
        if os.path.isfile(fullpath):
            #print fullpath
            ret = re.search(pat,f)
            if ret:
                gs = ret.groups()
                dealer_name = gs[0].decode('gbk')
                dealer_sn = gs[1]
                uf = f.decode('gbk')
                try:
                    d = Dealer.objects.get(name=dealer_sn)
                except Dealer.DoesNotExist:
                    print u'不存在 %s  %s' % (dealer_name,uf)
                    continue
                
                score = _read_xls_score(fullpath)
                print score
                
                xslpath = u'xls/2010/%s/%s' % (fname,uf)
                xls = XlsReportHist(dealer=d)
                xls.xlsfile = xslpath
                xls.term_index = termindex
                xls.score = score
                xls.save()

#读取分数字段
def _read_xls_score(xlspath):
    book = xlrd.open_workbook(xlspath)
    sh = book.sheet_by_index(0)
    rx = 10
    texts = sh.row_values(rx)
    #print texts
    return texts[17]
    
if __name__ == '__main__':
        
    t1 = time.clock()
    load_history()
    t2 = time.clock()
    print t2-t1
    
    #pat = ur'_([^_]*?)(\d+)_'
    #str1 = u'BMW MS 2010_Dealer Report_常州宝尊30649_1st Wave'
    #ret = re.search(pat,str1)
    #print ret
    #if ret:
    #    gs = ret.groups()
    #    print gs
