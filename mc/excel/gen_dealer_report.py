#encoding:utf-8

import os, sys, shutil
sys.path.insert(0, os.path.abspath(os.curdir))

import csv
from service.core._common import jinja_render_to_string
from service.core import _report

from mc import get_dealer_data
from mc.models import XslReport, Paper

from django.conf import settings

DEALER_REPORT_FOLDER = 'dealer_report'

script_path = os.path.dirname(os.path.abspath(__file__))

def _get_report_path():
    reportpath = os.path.join(settings.MEDIA_ROOT, DEALER_REPORT_FOLDER)
    if not os.path.exists(reportpath):
        os.makedirs(reportpath)
    return reportpath

def gen_dealer_report_file(paper):
    datadict = _report.get_dealer_data(paper)
    
#    tmpl_file = os.path.join(settings.SITE_ROOT, 'mc/excel/templates/Excel_Dealer_Report_%s Template_Q1_0401.xls' % paper.dealer.dealertype.name_en)
#    tmpl_file = os.path.join(settings.SITE_ROOT, 'mc/excel/templates/Excel_Dealer_Report_%s Template_Q2_0701.xls' % paper.dealer.dealertype.name_en)
    tmpl_file = os.path.join(settings.SITE_ROOT, 'mc/excel/templates/Excel_Dealer_Report_%s Template_Q3_0823.xls' % paper.dealer.dealertype.name_en)
#    tmpl_file = os.path.join(settings.SITE_ROOT, 'mc/excel/templates/Excel_Dealer_Report_%s Template_Q4.xls' % paper.dealer.dealertype.name_en)
    reportpath = _get_report_path()
    wv = paper.term.id % 4
    if wv == 0:
        wv = 4
    filename = '%s 2012 MS_%s_%s_W%d.xls' % (paper.dealer.dealertype.name_en, paper.dealer.name_cn, paper.dealer.name, wv)
    
    import pythoncom
    pythoncom.CoInitialize()
    
    xls_file = os.path.join(reportpath, filename)
    shutil.copy(tmpl_file, xls_file)
    
    xl = _open_xl()    
    xls_file = xls_file.replace('/', '\\')
    ss = xl.Workbooks.Open(xls_file) #必须是绝对路径
    ss.Visible = False
    
    try:
        fill_datasource(datadict, ss, paper, 4)
    finally:
        ss.Save()
        ss.Close()
    
    filepath = u'%s/%s' % (DEALER_REPORT_FOLDER, filename)
    #pythoncom.CoUninitialize()
    xl.Application.Quit()
    global win32_xl
    win32_xl = None
    return filepath

import time, os, sys, shutil
import win32com.client as win32

def set_color(cell):
    try:
        value = cell.Value
        s = float(value)
        s = int(s)
        if s < 99:
            cell.Font.ColorIndex = 5
            cell.Font.Bold = True
        else:
            cell.Font.ColorIndex = 1
            cell.Font.Bold = False
    except ValueError:
        cell.Font.ColorIndex = 5
        cell.Font.Bold = True

win32_xl = None
def _open_xl():    
    global win32_xl
    if win32_xl is None:
        xl = win32.gencache.EnsureDispatch('Excel.Application')
        xl.Visible = False
        xl.DisplayAlerts = False
        win32_xl = xl
    return win32_xl
    
def fill_datasource(datadict, ss, paper, sheet_number=1):
    term = paper.term
    dealertype = paper.dealer.dealertype
    sheet = ss.Sheets(sheet_number)
    
    dealer = datadict['dealer']
    #填入基本信息
    r = 'B1'
    sheet.Range(r).Value = dealer.name_cn
    r = 'B2'
    sheet.Range(r).Value = dealer.name
    r = 'C1'
    sheet.Range(r).Value = dealer.name_en
#    r = 'A15'
#    sheet.Range(r).Value = u'%s Dealer score' % dealer.name_cn
    r = 'B3'
    sheet.Range(r).Value = dealer.city_cn
    r = 'C3'
    sheet.Range(r).Value = dealer.city_en
    r = 'B4'
    sheet.Range(r).Value = dealer.province_cn
    r = 'C4'
    sheet.Range(r).Value = dealer.province_en
    r = 'B5'
    sheet.Range(r).Value = dealer.parent.parent.name_cn
    r = 'C5'
    sheet.Range(r).Value = dealer.parent.parent.name_en
    r = 'B6'
    sheet.Range(r).Value = datadict['curr_term'].score
    r = 'B7'
    sheet.Range(r).Value = datadict['begin_time']
    r = 'B8'
    sheet.Range(r).Value = datadict['end_time']
    r = 'B9'
    sheet.Range(r).Value = datadict['visit_time']
    
    CP_ROW_DICT = {'Total':15, 'A':26, 'B':39, 'C':53, 'D':66, 'E':78, 'F':90, 'G':104}
    TERM_LIST = ['B', 'C', 'D', 'E']
    CP_LIST = datadict['cp_list']
    #by basic 第一部分
    for cp in CP_LIST:
        #经销商分数
        row = CP_ROW_DICT[cp.name]
        for index, score in enumerate(cp.score_list):
            col = TERM_LIST[index]
            r = '%s%d' % (col, row)
            sheet.Range(r).Value = score
        #全国分数
        row += 1
        for index, score in enumerate(cp.score_list_nation):
            col = TERM_LIST[index]
            r = '%s%d' % (col, row)
            sheet.Range(r).Value = score
        #大区分数
        row += 1
        for index, score in enumerate(cp.score_list_daqu):
            col = TERM_LIST[index]
            r = '%s%d' % (col, row)
            sheet.Range(r).Value = score
        #小区分数
        row += 1
        for index, score in enumerate(cp.score_list_xq):
            col = TERM_LIST[index]
            r = '%s%d' % (col, row)
            sheet.Range(r).Value = score
        #省份分数
        row += 1
        for index, score in enumerate(cp.score_list_province):
            col = TERM_LIST[index]
            r = '%s%d' % (col, row)
            sheet.Range(r).Value = score
        #城市分数
        row += 1
        for index, score in enumerate(cp.score_list_city):
            col = TERM_LIST[index]
            r = '%s%d' % (col, row)
            sheet.Range(r).Value = score
        #经销商集团分数
        row += 1
        for index, score in enumerate(cp.score_list_jt):
            col = TERM_LIST[index]
            r = '%s%d' % (col, row)
            sheet.Range(r).Value = score

    #by basic 第二部分
    row = 114
    for cp in CP_LIST:
        if cp.name == 'G' or cp.name == 'Total':
            if 'G' in cp.name:
                for sub_cp in cp.sub_cp_list:
                    if 'G64' == sub_cp.name:
                        for index, score in enumerate(sub_cp.score_list):
                            col = TERM_LIST[index]
                            r = '%s234' % col
                            sheet.Range(r).Value = score
            continue
        for index, score in enumerate(cp.score_list):
            col = TERM_LIST[index]
            r = '%s%d' % (col, row)
            sheet.Range(r).Value = score
        row += 1
        for sub_cp in cp.sub_cp_list:
            for index, score in enumerate(sub_cp.score_list):
                col = TERM_LIST[index]
                r = '%s%d' % (col, row)
                sheet.Range(r).Value = score
            col = 'F'
            r = '%s%d' % (col, row)
            if sub_cp.zero_reason:
                txt = sub_cp.zero_reason
                if txt and txt.endswith('<br>'):
                    txt = txt[0:-4]
                if sub_cp.zero_reason_en:
                    txt = txt + '<br>' + sub_cp.zero_reason_en
                sheet.Range(r).Value = txt.replace('<br>', '\n')
            else:
                sheet.Range(r).Value = '-'
            row += 1
    
    #by question
    COL_LIST = ['B', 'C', 'D', 'E', 'F', 'G', 'H']
    row = 172
    cp_name = 'Z' # 起始判断过滤父检查点
    for cp in datadict['question_list']:
        if 'G' in cp.name:
            continue
        if cp_name not in cp.name_abbr:
            row += 1
            cp_name = cp.name_abbr[:1]
        col_index = 0
        col = COL_LIST[col_index]
        r = '%s%d' % (col, row)
        sheet.Range(r).Value = cp.score         #经销商分数
        col_index += 1
        col = COL_LIST[col_index]
        r = '%s%d' % (col, row)
        sheet.Range(r).Value = cp.score_nation  #全国分数
        col_index += 1
        col = COL_LIST[col_index]
        r = '%s%d' % (col, row)
        sheet.Range(r).Value = cp.score_daqu    #大区分数
        col_index += 1
        col = COL_LIST[col_index]
        r = '%s%d' % (col, row)
        sheet.Range(r).Value = cp.score_xq      #小区分数
        col_index += 1
        col = COL_LIST[col_index]
        r = '%s%d' % (col, row)
        sheet.Range(r).Value = cp.score_province#省份分数
        col_index += 1
        col = COL_LIST[col_index]
        r = '%s%d' % (col, row)
        sheet.Range(r).Value = cp.score_city    #城市分数
        col_index += 1
        col = COL_LIST[col_index]
        r = '%s%d' % (col, row)
        sheet.Range(r).Value = cp.score_jt      #集团分数
        row += 1
    
    #G50
#    sheet.Range('B231').Value = datadict['t3']
#    if dealertype.name_en == 'MINI':
#        sheet.Range('B223').Value = datadict['t3']
    
    #做的好的地方和做的不好的地方
    bads = datadict['bad_comments']
    goods = datadict['good_comments']
    bads_en = datadict['bad_comments_en']
    goods_en = datadict['good_comments_en']
    
    bad_comments = ''
    if bads:
        bad_comments = bads
        if bads_en:
            bad_comments += '\n'
            bad_comments += bads_en
    good_comments = ''
    if goods:
        good_comments = goods
        if goods_en:
            good_comments += '\n'
            good_comments += goods_en
    
    #sheet1 补漏
    sheet1 = ss.Sheets(1)
#    sheet1.Range('G208').Value = good_comments
#    sheet1.Range('G214').Value = bad_comments
    
    termstr = u'本期总得分(第%d期)：' % (term.id - 4)
    sheet1.Range('N11').Value = termstr
    termstr = u'Overall score of %dst wave' % (term.id - 4)
    sheet1.Range('N12').Value = termstr
    
    #sheet2 补漏
    sheet2 = ss.Sheets(2)
    
    #sheet3 补漏
    sheet3 = ss.Sheets(3)
    
    sheet3.Range('T284').Value = good_comments
    sheet3.Range('T295').Value = bad_comments
    
    if dealertype.name_en == 'MINI':
        rt3 = datadict.get('t3', '-')
        sheet3.Range('B306').Value = rt3.replace('<br>', '\n')
    #最终交车时间
    #预计交车时间
    repare_time = u'最终完工时间 final car delivery time: ' + datadict['repare_time']
    estimate_time = u'预计完工时间 completion deadline: ' + datadict['estimate_time']
    
    sheet3.Range('B184').Value = repare_time
    sheet3.Range('B139').Value = estimate_time
    
    #切换sheet
    sheet.Activate()
    sheet.Range('A1').Activate()
    
    sheet3.Activate()
    sheet3.Range('A1').Activate()
    sheet2.Activate()
    sheet2.Range('A1').Activate()
    
    sheet4 = ss.Sheets(4)
    sheet4.Visible = False


if __name__ == "__main__":
    paper = Paper.objects.get(id=951)
    datadict = _report.get_dealer_data(paper)
    for cp in datadict['question_list']:
        print cp
