#encoding:utf-8

import os,sys,shutil
sys.path.insert(0,os.path.abspath(os.curdir))

os.environ['DJANGO_SETTINGS_MODULE'] = r'settings'

from mc import get_dealer_data
from django.conf import settings

from mc.models import Term,Dealer
from mc import get_paper,enums

import win32com.client as win32

DEALER_REPORT_FOLDER = 'dealer_report'

def _index2colname(index):
    """
        1 -> 'A'
        2 -> 'B'
        26 -> 'Z'
        27 -> 'AA'
        52 -> 'AZ'
        53 -> 'BA'
    
    """
    if index > 26:
        index1 = (index - 1)/26
        index2 = index%26
        return _index2colname(index1) + _index2colname(index2)
    else:
        if index == 0:
            return 'Z'
        else:
            return chr(ord('A')+index-1)
    
#获得下一行的名称
def _get_next_colname(col):
    index2 = 0
    if len(col) > 1:
        f = col[0]
        s = col[1]
        index2 = ord(f) - ord('A') + 1
    else:
        s = col[0]
    
    index1 = ord(s) - ord('A') + 1
    index = index2 * 26 + index1
    #print index
    return _index2colname(index + 1)
    
#生成数据大表
def gen_big_data_table_func(term_id=0):
    if term_id == 0:
        term = mc.get_cur_term()
    else:
        term = Term.objects.get(id=term_id)
    
    xls_file = _get_export_file(term.id)
    ss = _open_excel_file(xls_file)
    
    try:
        dealer_list = Dealer.objects.filter(has_child=False)
        for dealer in dealer_list:
            print u'正在导出 %s' % dealer.name_cn
            
            datadict = get_dealer_data(dealer,curr_term=term)
            if not datadict:
                print u'%s 尚未有数据' % dealer.name_cn
                continue
            _write_one_dealer(dealer,datadict,ss,term.id-1)
    finally:
        ss.Save()
        ss.Close()

def _get_export_file(termid):
    tmpl_file = os.path.join(settings.SITE_ROOT,u'doc/from_customer/2011数据大表_Q3_模板0728.xls')
    reportpath = _get_report_path()
    filename = u'2011数据大表_Q%d.xls' % termid
    report_file = os.path.join(reportpath,filename)
    shutil.copy(tmpl_file, report_file)
    return report_file

def _get_report_path():
    reportpath = os.path.join(settings.MEDIA_ROOT,DEALER_REPORT_FOLDER)
    if not os.path.exists(reportpath):
        os.makedirs(reportpath)
    return reportpath

def _open_excel_file(xls_file):
    xl = win32.gencache.EnsureDispatch('Excel.Application')
    xl.Visible = False
    xl.DisplayAlerts = False
    
    xls_file = xls_file.replace('/','\\')
    
    ss = xl.Workbooks.Open(xls_file) #必须是绝对路径
    ss.Visible = False
    return ss

def _write_one_dealer(dealer,datadict,ss,term_index):
    dt = dealer.dealertype
    if dt.id == 1:
        sheet = ss.Sheets(1)
        sheet1 = ss.Sheets(2)
    else:
        sheet = ss.Sheets(3)
        sheet1 = ss.Sheets(4)
    
    #查找第几行
    line = _find_dealer_line(sheet,dealer.name)
    print dealer.name,line
    if line <= 0:
        return
    
    start_rows = {
        1:'L',
        2:'V',
        3:'AU',
        4:'BH',
    }
    cp_list = datadict['cp_list']
    index = 1
    for cp in cp_list[1:5]:
        sr = start_rows[index]
        index += 1
        for sub_cp in cp.sub_cp_list:
            r = '%s%s' % (sr, line)
            
            s = sub_cp.score_list[term_index]
            #~ print sub_cp,r
            #print 's = ',s,'r =',r
            sheet.Range(r).Value = s
            
            sr = _get_next_colname(sr)
    
    bads = datadict['bad_comments']
    goods = datadict['good_comments']
    score_comments = datadict['score_comments']
    
    #新加题答案
    r = '%s%s'%('L',line)
    sheet1.Range(r).Value = datadict['q_a52']
    r = '%s%s'%('M',line)
    sheet1.Range(r).Value = datadict['q_b53']
    r = '%s%s'%('N',line)
    sheet1.Range(r).Value = datadict['q_c54']
    r = '%s%s'%('O',line)
    sheet1.Range(r).Value = datadict['q_e55']
    
    
    r = '%s%s' % ('BP', line)
    sheet.Range(r).Value = goods
    r = '%s%s' % ('BQ', line)
    sheet.Range(r).Value = bads
    r = '%s%s' % ('BR', line)
    sheet.Range(r).Value = score_comments

#在文件中查找名称
def _find_dealer_line(sheet,dealername):
    lines = range(5,165)
    for line in lines:
        r = 'B%d' % line
        name = sheet.Range(r).Value
        if hasattr(name,'strip'):
            name = name.strip()
        elif name:
            name = str(int(name))
        else:
            continue
        
        if name == dealername:
            return line
    
    return 0

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'only one args need!'
        sys.exit()
    
    term_id = sys.argv[1]
    gen_big_data_table_func(term_id)
    
