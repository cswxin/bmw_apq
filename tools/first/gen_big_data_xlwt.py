#encoding:utf-8
import os, sys, shutil
sys.path.insert(0, os.path.abspath(os.curdir))
from mc.models import Question, PaperDiff, Dealer
from service.core._question import restore_result
import DbUtils
import xlrd
from service.core import _report, _paper, _term
from mc.models import XslReport, Paper
from survey.models import CheckPoint, Alternative, Translation
from django.conf import settings
from mc import enums
from survey.survey_utils import get_reportdata_dict_by_paper

BMW_num = 1
MINI_num = 1
COM_num = 1

BMW_q_dict = {'A':'K', 'A1':'L', 'A2':'M', 'A3':'N', 'A4':'O', 'A5':'P', 'A6':'Q', 'A7':'R',
          'B':'T', 'B8':'U', 'B9':'V', 'B10':'W', 'B11':'X', 'B12':'Y', 'B13':'Z', 'B14':'AA', 'B15':'AB', 'B16':'AC', 'B17':'AD', 'B18':'AE', 'B19':'AF', 'B20':'AG', 'B21':'AH', 'B22':'AI', 'B23':'AJ', 'B24':'AK',
          'C':'AM', 'C25':'AN', 'C26':'AO', 'C27':'AP', 'C28':'AQ', 'C29':'AR',
          'D':'AT', 'D30':'AU', 'D31':'AV', 'D32':'AW', 'D33':'AX', 'D34':'AY', 'D35':'AZ', 'D36':'BA', 'D37':'BB', 'D38':'BC', 'D39':'BD', 'D40':'BE', 'D41':'BF', 'D42':'BG',
          'E':'BI', 'E43':'BJ', 'E44':'BK', 'E45':'BL', 'E46':'BM',
          'F':'BO', 'F47':'BP', 'F48':'BQ',
          'G50__A1':'BS', 'G50__A2':'BT', 'G51__A1':'BU', 'G64':'BV'}

MINI_q_dict = {'A':'K', 'A1':'L', 'A2':'M', 'A3':'N', 'A4':'O', 'A5':'P', 'A6':'Q', 'A7':'R',
          'B':'T', 'B8':'U', 'B9':'V', 'B10':'W', 'B11':'X', 'B12':'Y', 'B13':'Z', 'B14':'AA', 'B15':'AB', 'B16':'AC', 'B17':'AD', 'B18':'AE', 'B19':'AF', 'B20':'AG', 'B21':'AH', 'B22':'AI', 'B23':'AJ', 'B24':'AK',
          'C':'AM', 'C25':'AN', 'C26':'AO', 'C27':'AP', 'C28':'AQ', 'C29':'AR',
          'D':'AT', 'D30':'AU', 'D31':'AV', 'D32':'AW', 'D33':'AX', 'D34':'AY', 'D35':'AZ', 'D36':'BA', 'D37':'BB', 'D38':'BC', 'D39':'BD', 'D40':'BE', 'D41':'BF', 'D42':'BG',
          'E':'BI', 'E43':'BJ', 'E44':'BK', 'E45':'BL', 'E46':'BM',
          'F':'BO', 'F47':'BP', 'F48':'BQ',
          'G50__A1':'BS', 'G50__A2':'BT', 'T3':'BU', 'G51__A1':'BV'}

Com_q_dict = {'A':'K', 'A1':'L', 'A2':'M', 'A3':'N', 'A4':'O', 'A7':'P',
          'B':'R', 'B8':'S', 'B9':'T', 'B10':'U', 'B11':'V', 'B12':'W', 'B13':'X', 'B14':'Y', 'B15':'Z', 'B16':'AA', 'B17':'AB', 'B19':'AC', 'B20':'AD', 'B21':'AE', 'B22':'AF', 'B24':'AG',
          'C':'AI', 'C25':'AJ', 'C26':'AK', 'C27':'AL', 'C28':'AM', 'C29':'AN',
          'D':'AP', 'D31':'AQ', 'D32':'AR', 'D33':'AS', 'D34':'AT', 'D35':'AU', 'D38':'AV', 'D40':'AW', 'D41':'AX', 'D42':'AY',
          'E':'BA', 'E43':'BB', 'E46':'BC',
          'G50__A1':'BE', 'G50__A2':'BF', 'G51__A1':'BG'}

def colname2index(colname):
    reverse = colname[::-1]
    ord_a = ord('A')
    num = 0
    import math
    for index, ch in enumerate(reverse):
        ord_ch = ord(ch) 
        num += ((ord_ch - ord_a) % 26 + 1) * math.pow(26, index)
    return int(num)

def write_data(term, template=u'big_data/2012年第1期数据大表_template.xls'):
    #tmpl_file = os.path.join(settings.SITE_ROOT, u'file/big_data/2012数据大表_Q1_0404.xls')
    tmpl_file = os.path.join(settings.RESOURCES_ROOT, template)
    xls_file = os.path.join(settings.RESOURCES_ROOT, u'big_data/%s_数据大表.xls' % term.name_cn)
    shutil.copy(tmpl_file, xls_file)
    
    from xlrd import open_workbook
    rb = open_workbook(tmpl_file, formatting_info=True)
    from xlutils.copy import copy2
    wbk, style_list = copy2(rb)
    
    sheets = rb.sheets();
    for idx, rbsheet in enumerate(sheets):
        sheet = wbk.get_sheet(idx)
        rows = rbsheet.nrows
        for rx in range(0, rows):
            texts = rbsheet.row_values(rx)
            for colx, cx in enumerate(texts):
                datastyle = style_list[rbsheet.cell_xf_index(rx, colx)]
                sheet.write(rx, colx, cx, datastyle)
                
    BMW_startline = 4
    MINI_startline = 4
#    BMW_daqu_line_dict = {'East':5, 'North':66, 'South':112, 'West':152}
#    MINI_daqu_line_dict = {'East':5, 'North':10, 'South':13, 'West':16}
    daqu_dealers = Dealer.objects.filter(level=1).order_by('id') # East, North, South, West
    
    try:
        for daqu in daqu_dealers:
            BMW_dealers = term.dealers.filter(dealertype__id=1, level=3, parent__parent=daqu)
            print 'BMW', daqu.name, 'startline:', BMW_startline, 'count:', len(BMW_dealers)
            for dealer in BMW_dealers:
                BMW_startline = gen_excel_sheet1(dealer, wbk, rb, style_list, BMW_startline, daqu, 2, BMW_q_dict, 'GFK', term)
            BMW_startline += 1
            
                
            MINI_dealers = term.dealers.filter(dealertype__id=5, level=3, parent__parent=daqu)
            print 'MINI', daqu.name, 'startline:', MINI_startline, 'count:', len(MINI_dealers)
            for dealer in MINI_dealers:
                MINI_startline = gen_excel_sheet1(dealer, wbk, rb, style_list, MINI_startline, daqu, 3, MINI_q_dict, 'GFK', term)
            MINI_startline += 1
            
        audi_dealers = term.dealers.filter(dealertype__id=3, level=3).order_by('name')
        audi_startline = 4
        print 'AUDI startline:', audi_startline, 'count:', len(audi_dealers)
        for dealer in audi_dealers:
            papers = Paper.objects.filter(dealer=dealer, project__id=4, paper_type='GFK', term=term, status=100)
#            if papers and len(papers) > 0:
#                dealers = []
#                dealers.extend(term.dealers.all())
#                dealers.append(dealer)
#                term.dealers = dealers
#                term.save()
            audi_startline = gen_excel_sheet_com(dealer, wbk, rb, style_list, audi_startline, 4, Com_q_dict, 'GFK', term)
        lexus_dealers = term.dealers.filter(dealertype__id=4, level=3).order_by('name')
        lexus_startline = audi_startline + 1
        print 'LEXUS startline:', lexus_startline, 'count:', len(lexus_dealers)
        for dealer in lexus_dealers:
            papers = Paper.objects.filter(dealer=dealer, project__id=4, paper_type='GFK', term=term, status=100)
#            if papers and len(papers) > 0:
#                dealers = []
#                dealers.extend(term.dealers.all())
#                dealers.append(dealer)
#                term.dealers = dealers
#                term.save()
            lexus_startline = gen_excel_sheet_com(dealer, wbk, rb, style_list, lexus_startline, 4, Com_q_dict, 'GFK', term)
        benz_dealers = term.dealers.filter(dealertype__id=2, level=3).order_by('name')
        benz_startline = lexus_startline + 1
        print 'BENZ startline:', benz_startline, 'count:', len(benz_dealers)
        for dealer in benz_dealers:
            papers = Paper.objects.filter(dealer=dealer, project__id=4, paper_type='GFK', term=term, status=100)
#            if papers and len(papers) > 0:
#                dealers = []
#                dealers.extend(term.dealers.all())
#                dealers.append(dealer)
#                term.dealers = dealers
#                term.save()
            benz_startline = gen_excel_sheet_com(dealer, wbk, rb, style_list, benz_startline, 4, Com_q_dict, 'GFK', term)
    finally:
        wbk.save(xls_file)
    return xls_file


col_dict = {'no':'A', 'dealer_code':'B', 'city':'C', 'province':'D', 'region':'E', 'name_cn':'F', 'name_en':'G', 'total':'I'}

def gen_excel_sheet_com(dealer, wbk, rb, style_list, startline, project_id, q_dict, paper_type, term):
    global BMW_num
    global MINI_num
    global COM_num
    sheet = wbk.get_sheet(project_id - 2)
    rbsheet = rb.sheet_by_index(project_id - 2)
    colnum = colname2index(col_dict['no'])
    datastyle = style_list[rbsheet.cell_xf_index(startline, colnum - 1)]
    if project_id == 2:
        sheet.write(startline, colnum - 1, BMW_num, datastyle)
    elif project_id == 3:
        sheet.write(startline, colnum - 1, MINI_num, datastyle)
    elif project_id == 4:
        sheet.write(startline, colnum - 1, COM_num, datastyle)
    colnum = colname2index(col_dict['dealer_code'])
    datastyle = style_list[rbsheet.cell_xf_index(startline, colnum - 1)]
    sheet.write(startline, colnum - 1, dealer.name, datastyle)
    colnum = colname2index(col_dict['city'])
    datastyle = style_list[rbsheet.cell_xf_index(startline, colnum - 1)]
    sheet.write(startline, colnum - 1, dealer.city_cn, datastyle)
    colnum = colname2index(col_dict['province'])
    datastyle = style_list[rbsheet.cell_xf_index(startline, colnum - 1)]
    sheet.write(startline, colnum - 1, dealer.province_cn, datastyle)
    colnum = colname2index(col_dict['region'])
    datastyle = style_list[rbsheet.cell_xf_index(startline, colnum - 1)]
    sheet.write(startline, colnum - 1, dealer.parent.name, datastyle)
    colnum = colname2index(col_dict['name_cn'])
    datastyle = style_list[rbsheet.cell_xf_index(startline, colnum - 1)]
    sheet.write(startline, colnum - 1, dealer.name_cn, datastyle)
    colnum = colname2index(col_dict['name_en'])
    datastyle = style_list[rbsheet.cell_xf_index(startline, colnum - 1)]
    sheet.write(startline, colnum - 1, dealer.name_en, datastyle)
    colnum = colname2index(col_dict['total'])
    papers = Paper.objects.filter(dealer=dealer, project__id=project_id, paper_type=paper_type, term=term, status=100)
    if papers:
        paper = papers[0]
        score = paper.score
        #sheet.Range(r).Value = score
        reportdata_dict = get_reportdata_dict_by_paper(paper)
        for k, col in q_dict.items():
            if k in ['A', 'B', 'C', 'D', 'E', 'F']:
                continue
            colnum = colname2index(col)
#            print  r, k
            if 'G' in k or 'T3' == k:
                sub_score = paper.respondent.get_data(k)
                if 'G64' == k:
                    sub_score = Alternative.objects.get(id=sub_score).title
                datastyle = style_list[rbsheet.cell_xf_index(startline, colnum - 1)]
                sheet.write(startline, colnum - 1, sub_score, datastyle)
            else:
                cp = CheckPoint.objects.get(name_abbr=k, project=paper.project)
                
                if not reportdata_dict:
                    print 'noooooo--->', k, paper.respondent.id
                if reportdata_dict:
                    sub_score = reportdata_dict[cp.name]
                    if sub_score == '' or sub_score is None:
                        sub_score = u'不适用'
                    datastyle = style_list[rbsheet.cell_xf_index(startline, colnum - 1)]
                    sheet.write(startline, colnum - 1, sub_score, datastyle)
#                print cp.name, sub_score
    
    if project_id == 2:
        BMW_num += 1
    elif project_id == 3:
        MINI_num += 1
    elif project_id == 4:
        COM_num += 1
        
    startline += 1
    
    return startline
    
def gen_excel_sheet1(dealer, wbk, rb, style_list, startline, daqu, project_id, q_dict, paper_type, term):
    global BMW_num
    global MINI_num
    global COM_num
    sheet = wbk.get_sheet(project_id - 2)
    rbsheet = rb.sheet_by_index(project_id - 2)
    colnum = colname2index(col_dict['no'])
    datastyle = style_list[rbsheet.cell_xf_index(startline, colnum - 1)]
    if project_id == 2:
        sheet.write(startline, colnum - 1, BMW_num, datastyle)
    elif project_id == 3:
        sheet.write(startline, colnum - 1, MINI_num, datastyle)
    elif project_id == 4:
        sheet.write(startline, colnum - 1, COM_num, datastyle)
    colnum = colname2index(col_dict['dealer_code'])
    datastyle = style_list[rbsheet.cell_xf_index(startline, colnum - 1)]
    sheet.write(startline, colnum - 1, dealer.name, datastyle)
    colnum = colname2index(col_dict['city'])
    datastyle = style_list[rbsheet.cell_xf_index(startline, colnum - 1)]
    sheet.write(startline, colnum - 1, dealer.city_cn, datastyle)
    colnum = colname2index(col_dict['province'])
    datastyle = style_list[rbsheet.cell_xf_index(startline, colnum - 1)]
    sheet.write(startline, colnum - 1, dealer.province_cn, datastyle)
    colnum = colname2index(col_dict['region'])
    datastyle = style_list[rbsheet.cell_xf_index(startline, colnum - 1)]
    sheet.write(startline, colnum - 1, daqu.name, datastyle)
    colnum = colname2index(col_dict['name_cn'])
    datastyle = style_list[rbsheet.cell_xf_index(startline, colnum - 1)]
    sheet.write(startline, colnum - 1, dealer.name_cn, datastyle)
    colnum = colname2index(col_dict['name_en'])
    datastyle = style_list[rbsheet.cell_xf_index(startline, colnum - 1)]
    sheet.write(startline, colnum - 1, dealer.name_en, datastyle)
    colnum = colname2index(col_dict['total'])
    
    papers = Paper.objects.filter(dealer=dealer, project__id=project_id, paper_type=paper_type, term=term, status=100)
    if papers:
        paper = papers[0]
        score = paper.score
        #sheet.Range(r).Value = score
        reportdata_dict = get_reportdata_dict_by_paper(paper)
        for k, col in q_dict.items():
            if k in ['A', 'B', 'C', 'D', 'E', 'F']:
                continue
            colnum = colname2index(col)
            if 'G' in k or 'T3' == k:
                sub_score = paper.respondent.get_data(k)
                if 'G64' == k:
                    sub_score = Alternative.objects.get(id=sub_score).title
                datastyle = style_list[rbsheet.cell_xf_index(startline, colnum - 1)]
                sheet.write(startline, colnum - 1, sub_score, datastyle)
            else:
                cp = CheckPoint.objects.get(name_abbr=k, project=paper.project)
                if not reportdata_dict:
                    print 'noooooo--->', k, paper.respondent.id
                if reportdata_dict:
                    sub_score = reportdata_dict[cp.name]
                    if sub_score == '' or sub_score is None:
                        sub_score = u'不适用'
                    datastyle = style_list[rbsheet.cell_xf_index(startline, colnum - 1)]
                    sheet.write(startline, colnum - 1, sub_score, datastyle)
    
    if project_id == 2:
        BMW_num += 1
    elif project_id == 3:
        MINI_num += 1
    elif project_id == 4:
        COM_num += 1
        
    startline += 1
    
    return startline

if __name__ == '__main__':
    term = _term.get_term_by_id(7)
    templateName = u'big_data/%s数据大表_template.xls' % term.name_cn
    write_data(term, templateName)
    
