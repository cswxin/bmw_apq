#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys

sys.path.insert(0, os.path.abspath(os.curdir))
import settings

from mc.models import Term, Report, Dealer, DealerType
from survey.models import Question, Project
import DbUtils
import cStringIO
import cPickle as pickle
from json import encoder
encoder.FLOAT_REPR = lambda o: format(o, '.6f')

def handleScore(score):
    if isinstance(score, (int, float)):
        return float(str('%0.15g' % score))
    if score.find(u'——') != -1:
        print score
    return None

def pyobj_to_str(pyobj):
    '''将对象序列化'''
    buffers = cStringIO.StringIO()
    pickle.dump(pyobj, buffers)
    return buffers.getvalue()

def str_to_pyobj(astr):
    '''将字符串转成对象'''
    if isinstance(astr, unicode):
        buffers = cStringIO.StringIO(astr.encode('utf-8'))
    else:
        buffers = cStringIO.StringIO(astr)
    pyobj = pickle.load(buffers)
    buffers.close()
    return pyobj

def parse_answer(answer):
    if isinstance(answer, unicode):
        return answer
    elif isinstance(answer, str):
        return answer.decode('utf-8')
    return str(answer)

def colname2index(colname):
    reverse = colname[::-1]
    ord_a = ord('A')
    num = 0
    import math
    for index, ch in enumerate(reverse):
        ord_ch = ord(ch)
        num += ((ord_ch - ord_a) % 26 + 1) * math.pow(26, index)
    return int(num) - 1

def index2colname(celNum):
    '''列的索引值对应字母表示值
    '''
    num = celNum + 1 #celNum是从0算起
    tem = ""
    ord_a = ord('A')
    while(num > 0):
        lo = (num - 1) % 26 #//取余，A到Z是26进制，
        tem = chr(lo + ord_a) + tem
        num = (num - 1) / 26 #//取模
    return tem

def import_data_s1(project, dealertype, sh):
    rows = sh.nrows
    ncols = sh.ncols

    sheet_value = []
    for col in range(0, ncols):
        cid = sh.row(0)[col].value
        if cid:
            sheet_value.append((cid, col))

    for rownum in range(3, rows):
        dealer_code = sh.cell(rownum, 0).value
        dealer = None
        if isinstance(dealer_code, (int, float)):
            dealer_code = '%s' % int(dealer_code)
            if dealer_code:
                dealer = Dealer.objects.get(name=dealer_code, dealertype=dealertype)
        if not dealer_code:
            dealer_code = sh.cell(rownum, 3).value
            if dealer_code:
                dealer = Dealer.objects.get(name=dealer_code)
        if not dealer:
            continue
        print dealer_code
#        if dealer_code == '33459':
#            continue
        score = sh.cell(rownum, 6).value
        part_a = sh.cell(rownum, 7).value
        part_b = sh.cell(rownum, 10).value

        score_dict = {}
        for cid, col in sheet_value:
            value = sh.cell(rownum, col).value
            if isinstance(value, (int, float)):
                value = handleScore(value)
            score_dict[cid] = value
        score_str = pyobj_to_str(score_dict)

        report = Report.objects.get_or_create(project=project, dealer=dealer, term=term , dealertype=dealertype)[0]
        report.dealer_name = dealer.name
        report.term_name = term.name
        report.score = score
        report.part_a = part_a
        report.part_b = part_b
        report.score_str = score_str
        report.save()

def add_answer_dict(answer_dict, qid, score):
    if score == 0:
        answer_dict['%s' % qid] = u'否'
    if score == 100:
        answer_dict['%s' % qid] = u'是'
    if score == '/':
        #ycf 2014-12-15 不适用全部改为不涉及
        answer_dict['%s' % qid] = u'不涉及'

def import_data_s2(project, dealertype, sh):
    rows = sh.nrows
    ncols = sh.ncols

    sheet_value = []
    for col in range(0, ncols):
        cid = sh.row(0)[col].value
        if cid:
            sheet_value.append((cid, col))

    for rownum in range(3, rows):
#        print rownum

        dealer_code = sh.cell(rownum, 0).value
        dealer = None
        if isinstance(dealer_code, (int, float)):
            dealer_code = '%s' % int(dealer_code)
            if dealer_code:
                dealer = Dealer.objects.get(name=dealer_code, dealertype=dealertype)
        if not dealer_code:
            dealer_code = sh.cell(rownum, 3).value
            if dealer_code:
                dealer = Dealer.objects.get(name=dealer_code)
        if not dealer:
            continue
        print dealer_code
#        if dealer_code == '33459':
#            continue
        score = sh.cell(rownum, 8).value
        part_a = sh.cell(rownum, 11).value
        part_b = sh.cell(rownum, 14).value

        answer_dict = {}
        for cid, col in sheet_value:
            answer_dict[cid] = sh.cell(rownum, col).value

        report = Report.objects.get_or_create(project=project, dealer=dealer, term=term , dealertype=dealertype)[0]
        report.dealer_name = dealer.name
        report.term_name = term.name
        report.score = score
        report.part_a = part_a
        report.part_b = part_b

        score_dict = {}
        score_str = report.score_str
        if score_str:
            score_dict = str_to_pyobj(score_str)
            Q65 = score_dict.get('Q65')
            Q66 = score_dict.get('Q66')
            Q67 = score_dict.get('Q67')
            add_answer_dict(answer_dict, 'Q65', Q65)
            add_answer_dict(answer_dict, 'Q66', Q66)
            add_answer_dict(answer_dict, 'Q67', Q67)

        answer_str = pyobj_to_str(answer_dict)
        report.answer_str = answer_str
        report.save()

def excel2report(term, dtype):
    from xlrd import open_workbook
    if dtype == 'bmw':
        xls_file_name = u'得分数据大表_Q1_20150330_with raw data_BMW-爱调研.xls'
        project = Project.objects.get(id=3)
        dealertype = DealerType.objects.get(name_cn='BMW')
    elif dtype == 'mini':
        xls_file_name = u'得分数据大表_Q1_20150327_with raw data_MINI-爱调研.xls'
        project = Project.objects.get(id=4)
        dealertype = DealerType.objects.get(name_cn='MINI')

    xls_file = u'%s/doc/%s' % (settings.REL_SITE_ROOT, xls_file_name)

    wb = open_workbook(xls_file, formatting_info=True)
    sheets = wb.sheets()
    sh1 = sheets[0]
    sh2 = sheets[1]

    import_data_s1(project, dealertype, sh1)
    import_data_s2(project, dealertype, sh2)


if __name__ == '__main__':
    term = Term.objects.get(id=5)
    excel2report(term, 'bmw')
#    excel2report(term, 'mini')
