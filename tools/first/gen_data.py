#encoding:utf-8
import os, sys, shutil
sys.path.insert(0, os.path.abspath(os.curdir))
from mc.models import Question, PaperDiff, Dealer
from service.core._question import restore_result
import DbUtils
import xlrd
from service.core import _report, _paper
from mc.models import XslReport, Paper
from survey.models import CheckPoint, Alternative, Translation
from django.conf import settings
from survey import survey_utils
from mc import enums

import win32com.client as win32
win32_xl = None
def _open_xl():    
    global win32_xl
    if win32_xl is None:
        xl = win32.gencache.EnsureDispatch('Excel.Application')
        xl.Visible = False
        xl.DisplayAlerts = False
        win32_xl = xl
    return win32_xl

def write_data():
    import pythoncom
    pythoncom.CoInitialize()
    
    tmpl_file = os.path.join(settings.RESOURCES_ROOT, 'data/temp.xls')
    xls_file = os.path.join(settings.RESOURCES_ROOT, 'data/data.xls')
    shutil.copy(tmpl_file, xls_file)
    xl = _open_xl()
    xls_file = xls_file.replace('/', '\\')
    ss = xl.Workbooks.Open(xls_file) #必须是绝对路径
    ss.Visible = False
    
    startline = 2
    daqu_dealers = Dealer.objects.filter(level=1).order_by('id')
    try:
        for daqu in daqu_dealers:
            startline = gen_excel_sheet1(daqu, ss, startline, need_score=False)
            BMW_dealers = Dealer.objects.filter(dealertype__id=1, level=3, parent__parent=daqu)
            for dealer in BMW_dealers:
                startline = gen_excel_sheet1(dealer, ss, startline)
    finally:
        ss.Save()
        ss.Close()
        xl.Application.Quit()
        global win32_xl
        win32_xl = None

col_dict = {'dealer_code':'A', 'dealer_name_cn':'B', 'total':'C'}
def gen_excel_sheet1(dealer, ss, startline, need_score=True):
    sheet = ss.Sheets(1)
    if not need_score:
        r = '%s%s' % (col_dict['dealer_code'], startline)
        sheet.Range(r).Value = dealer.name
        r = '%s%s' % (col_dict['dealer_name_cn'], startline)
        sheet.Range(r).Value = dealer.name_cn
        startline += 1
    else:
        r = '%s%s' % (col_dict['dealer_code'], startline)
        sheet.Range(r).Value = dealer.name
        r = '%s%s' % (col_dict['dealer_name_cn'], startline)
        sheet.Range(r).Value = dealer.name_cn
        r = '%s%s' % (col_dict['total'], startline)
        papers = Paper.objects.filter(dealer=dealer, project__id=2, paper_type='BMW', term__id=5)
        if papers:
            score = papers[0].score
            sheet.Range(r).Value = score
        startline += 1
    return startline

if __name__ == '__main__':
    write_data()
