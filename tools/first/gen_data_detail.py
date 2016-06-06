#encoding:utf-8

import os, sys, shutil
sys.path.insert(0, os.path.abspath(os.curdir))

from django.conf import settings

from mc.models import Term, Dealer, Paper
from survey.models import Alternative, Question, Project, CheckPoint
from service.core import _report, _paper, _term
import constant
import xlwt
from django.db import connection
from survey.survey_utils import get_respondentdata_dict_by_paper

respondent_field_dict = {}

#生成数据大表
def gen_data_func(term):    
    xls_file = _get_export_file(term)
    wbk = _open_excel_file(xls_file)
    try:
        row1 = 1
        row2 = 1
        row3 = 1
        bmw_dealer_list = term.dealers.filter(dealertype__id=1)
        q1_list = respondent_field_dict[constant.current_project_id]
        for index, dealer in  enumerate(bmw_dealer_list):
            print u'正在导出BMW %s' % dealer.name_cn
            papers = Paper.objects.filter(dealer=dealer, project__id=constant.current_project_id, paper_type='GFK', term=term)
            respondentdata_dict = []
            if papers:
                paper = papers[0]
                respondentdata_dict = get_respondentdata_dict_by_paper(paper)
            sheet = wbk.get_sheet(0)
            row = row1 + index
            _write_one_dealer(dealer, term, respondentdata_dict, sheet, row, q1_list)
                
        #mini
        mini_dealer_list = term.dealers.filter(dealertype__id=5)
        q2_list = respondent_field_dict[constant.current_mini_project_id]
        for index, dealer in  enumerate(mini_dealer_list):
            print u'正在导出MINI %s' % dealer.name_cn
            papers = Paper.objects.filter(dealer=dealer, project__id=constant.current_mini_project_id, paper_type='GFK', term=term)
            respondentdata_dict = []
            if papers:
                paper = papers[0]
                respondentdata_dict = get_respondentdata_dict_by_paper(paper)
            sheet = wbk.get_sheet(1)
            row = row2 + index
            _write_one_dealer(dealer, term, respondentdata_dict, sheet, row, q2_list)
        
        #竞品
        com_dealer_list = term.dealers.filter(dealertype__id__in=[2, 3, 4]).order_by('name')
        q3_list = respondent_field_dict[constant.competition_project_id]
        for index, dealer in  enumerate(com_dealer_list):
            print u'正在导出竞品 %s' % dealer.name_cn
            papers = Paper.objects.filter(dealer=dealer, project__id=constant.competition_project_id, paper_type='GFK', term=term)
            respondentdata_dict = []
            if papers:
                paper = papers[0]
                respondentdata_dict = get_respondentdata_dict_by_paper(paper)
            sheet = wbk.get_sheet(2)
            row = row3 + index
            _write_one_dealer(dealer, term, respondentdata_dict, sheet, row, q3_list)
    finally:
        wbk.save(xls_file)

def _get_export_file(term):
    filename = u'big_data/%s_问卷_信息.xls' % term.name_cn
    report_file = os.path.join(settings.RESOURCES_ROOT, filename)
    return report_file

def _open_excel_file(xls_file):
    wbk = xlwt.Workbook()
    sheet1 = wbk.add_sheet(u'宝马问卷列表', cell_overwrite_ok=True)
    sheet2 = wbk.add_sheet(u'MINI问卷列表', cell_overwrite_ok=True)
    sheet3 = wbk.add_sheet(u'竞品问卷列表', cell_overwrite_ok=True)
    fs = _get_field_list()
    
    index = 0
    q1_list = Question.objects.filter(project__id=constant.current_project_id)
    q2_list = Question.objects.filter(project__id=constant.current_mini_project_id)
    q3_list = Question.objects.filter(project__id=constant.competition_project_id)
    
    respondent_field_dict[constant.current_project_id] = q1_list
    respondent_field_dict[constant.current_mini_project_id] = q2_list
    respondent_field_dict[constant.competition_project_id] = q3_list
    
    names_list = [u'期数', u'经销商名称', u'经销商地址', u'经销商编号']
    for f in names_list:
        sheet1.write(0, index, f)
        sheet2.write(0, index, f)
        sheet3.write(0, index, f)
        index += 1
    index1 = index
    index2 = index
    index3 = index
    for col, q in enumerate(q1_list):
        cps = CheckPoint.objects.filter(question=q)
        if q.name_abbr == 'G49':
            sheet1.write(0, index1 + col, 'G49a')
            index1 += 1
            sheet1.write(0, index1 + col, 'G49b')
        elif q.name_abbr in ['F48a', 'F48b', 'F48c', 'F48d']:
            for i in range(1, 5):
                sheet1.write(0, index1 + col, '%s__A%s' % (q.name_abbr, i))
                if i != 4:
                    index1 += 1
        else:
            sheet1.write(0, index1 + col, q.name_abbr)
        colum = q.cid
        if cps and len(cps) > 0:
            if cps[0].resp_col:
                colum = cps[0].resp_col
        open = '%s__open' % colum
        if open in fs:
            index1 += 1
            sheet1.write(0, index1 + col , open)
        #胎压
        f49_blank = ''
            
    for col, q in enumerate(q2_list):
        if q.name_abbr == 'G49':
            sheet2.write(0, index2 + col, 'G49a')
            index2 += 1
            sheet2.write(0, index2 + col, 'G49b')
        elif q.name_abbr in ['F48a', 'F48b', 'F48c', 'F48d']:
            for i in range(1, 5):
                sheet2.write(0, index2 + col, '%s__A%s' % (q.name_abbr, i))
                if i != 4:
                    index2 += 1
        else:
            sheet2.write(0, index2 + col, q.name_abbr)
        cps = CheckPoint.objects.filter(question=q)
        colum = q.cid
        if cps and len(cps) > 0:
            if cps[0].resp_col:
                colum = cps[0].resp_col
        open = '%s__open' % colum
        if open in fs:
            index2 += 1
            sheet2.write(0, index2 + col , open)
    for col, q in enumerate(q3_list):
        if q.name_abbr == 'G49':
            sheet3.write(0, index3 + col, 'G49a')
            index3 += 1
            sheet3.write(0, index3 + col, 'G49b')
        else:
            sheet3.write(0, index3 + col, q.name_abbr) 
        cps = CheckPoint.objects.filter(question=q)
        colum = q.cid
        if cps and len(cps) > 0:
            if cps[0].resp_col:
                colum = cps[0].resp_col
        open = '%s__open' % colum
        if open in fs:
            index3 += 1
            sheet3.write(0, index3 + col , open)
        
    return wbk

def _get_field_list():
    no_fs_list = ['term_id', 'dealer_code', 'appraiser_code', 'customer_code', 'id']
    sql = 'select * from survey_respondentdata where id =1;'
    import DbUtils
    try:
        c, con = DbUtils.cursor()
        c.execute(sql)
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
def _write_one_dealer(dealer, term, data, sheet, row, question_list):
    sheet.write(row, 0, term.name_cn)
    sheet.write(row, 1, dealer.name_cn)
    sheet.write(row, 2, dealer.address)
    sheet.write(row, 3, dealer.name)
    
    index = 4
    if data:
        for q in question_list:
            cps = CheckPoint.objects.filter(question=q)
            colum = q.cid
            if cps and len(cps) > 0:
                if cps[0].resp_col:
                    colum = cps[0].resp_col
            if q.name_abbr == 'G49':
                colum = 'G50__A1'
                val = data.get(colum, '')
                sheet.write(row, index, val)
                index += 1
                colum = 'G50__A2'
                val = data.get(colum, '')
                sheet.write(row, index, val)
                index += 1
            elif q.name_abbr in ['F48a', 'F48b', 'F48c', 'F48d']:
                for i in range(1, 5):
                    colum = '%s__A%s' % (q.cid, i)
                    val = data.get(colum, '')
                    sheet.write(row, index, val)
                    index += 1
            else:
                val = data.get(colum, '')
                sheet.write(row, index, val)
                index += 1
                open = '%s__open' % colum
                if data.has_key(open):
                    val = data.get(open, '')
                    sheet.write(row, index, val)
                    index += 1
    
if __name__ == '__main__':
    term = _term.get_cur_term()
    gen_data_func(term)
