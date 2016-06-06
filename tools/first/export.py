#encoding:utf-8
import os, sys, shutil
sys.path.insert(0, os.path.abspath(os.curdir))
from mc.models import Question, PaperDiff
from service.core._question import restore_result
import DbUtils
import xlrd
from service.core import _report, _paper, _term
from mc.models import XslReport, Paper
from survey.models import CheckPoint, Alternative, Translation
from django.conf import settings
from survey import survey_utils
from mc import enums
from service.easyExcel import easyExcel
import logging  
logging.basicConfig(filename=os.path.join(os.getcwd(), 'log.txt'), level=logging.WARN, filemode='w', format='%(asctime)s - %(levelname)s: %(message)s') 

def export():
    sqls = 'select distinct mp.id, md.name as dealercode, md.name_cn,"  B18" as " B18" , sa1.title , sa1.score ,B21a__open, "  D39" as " D39" , sa2.title , sa2.score ,D63__open from survey_respondentdata srd, mc_paper mp, mc_dealer md, mc_term_dealers mtd LEFT JOIN survey_alternative sa1 ON sa1.id = B21a LEFT JOIN survey_alternative sa2 ON sa2.id = D63 where  mp.respondent_id = srd.id and mp.project_id = 2 and mp.paper_type in ("GFK") and md.id = mp.dealer_id and mtd.dealer_id = mp.dealer_id and mtd.term_id = mp.term_id'
    c, db = DbUtils.cursor()
    c.execute(sqls)
    result = c.fetchall()
    data_list = []
    b18 = Question.objects.get(cid='B21a', project__id=2)
    d39 = Question.objects.get(cid='D63', project__id=2)
    index = 0
    for data in result:
        item = Item()
        item.dealer_code = data[1]
        item.dealer_name = data[2]
        item.B18_name = data[3]
        item.B18_value = data[4]
        item.B18_score = data[5]
        B18_open = data[6]
        if B18_open is not  None and  B18_open != '':
            B18_open = restore_result(b18, B18_open)
            B18_open = B18_open.replace('<br>', '')
        else:
            B18_open = ''
        item.D39_name = data[7]
        item.D39_value = data[8]
        item.D39_score = data[9]
        D39_open = data[10]
        if D39_open is not  None and  D39_open != '':
            D39_open = restore_result(d39, D39_open)
            D39_open = D39_open.replace('<br>', '')
        else:
            D39_open = ''
        #print  data[1], ',', data[2], ',', data[3], ',', data[4], ',', data[5], ',', B18_open, ',', data[7], ',', data[8], ',', data[9], ',', D39_open
        
        msg = 'UserProfile and LoginLogout will be deleted. Sure? (y/n):'
#        if  index % 100 == 0 and'y' == raw_input(msg):
#            continue
        index += 1

def write_data(term, showTran):
    
    tmpl_file = os.path.join(settings.RESOURCES_ROOT, 'temp.xls')
    needs = 'need'
    if showTran:
        needs = 'all'
    xls_file = os.path.join(settings.RESOURCES_ROOT, u'%s_tran_%s.xls' % (term.name_cn, needs))
    shutil.copy(tmpl_file, xls_file)
    xls_file = xls_file.replace('/', '\\')
    excel = easyExcel(xls_file)
    
    BMW_cp = CheckPoint.objects.filter(project__id=2, has_child=False)
    MINI_cp = CheckPoint.objects.filter(project__id=3, has_child=False)
    COM_cp = CheckPoint.objects.filter(project__id=4, has_child=False)
    startline = 3
    sh2_line = 3
    
    BMW_pds = PaperDiff.objects.filter(final_paper__dealer__dealertype__id=1, final_paper__term=term).exclude(status=3)
    BMW_papers = []
    for pd in BMW_pds:
        BMW_papers.append(pd.final_paper)
    
    MINI_pds = PaperDiff.objects.filter(final_paper__dealer__dealertype__id=5, final_paper__term=term).exclude(status=3)
    MINI_papers = []
    for pd in MINI_pds:
        MINI_papers.append(pd.final_paper)
        
    COM_pds = Paper.objects.filter(project__id=4, term=term, paper_type='GFK', status=enums.PAPER_STATUS_FINISH, dealer__dealertype__id__in=[2, 3, 4])
    COM_papers = COM_pds
    
    try:
        for paper in BMW_papers:
            startline, sh2_line = gen_excel_sheet1(paper, excel, startline, sh2_line, BMW_cp, showTran)
        for paper in MINI_papers:
            startline, sh2_line = gen_excel_sheet1(paper, excel, startline, sh2_line, MINI_cp, showTran)
        for paper in COM_papers:
            startline, sh2_line = gen_excel_sheet1(paper, excel, startline, sh2_line, COM_cp, showTran)
    finally:
        excel.save()
        excel.close()
    return xls_file

col_dict = {'paper_id':'A', 'dealer_code':'B', 'dealer_name_cn':'C', 'q_abbr':'D', 'q_title':'E', 'alt_title':'F', 'alt_reason':'G'}
def gen_excel_sheet1(paper, excel, startline, sh2_line, cp_list, showTran=False):
    ans_dict = survey_utils.get_respondentdata_dict_by_paper(paper)
    sh2_line = gen_excel_open(excel, ans_dict, paper, sh2_line, showTran)#开放题
    for cp in cp_list:
        if cp.question.questiontype == 2:
            if isinstance(ans_dict[cp.question.cid], (int, long)):
                if 'G51' in cp.question.name_abbr:
                    continue
                alt = Alternative.objects.get(id=ans_dict[cp.question.cid])
                
                if alt.title == u'否' or alt.title == u'不适用':
                    content_en = ''
                    need_tran = False
                    trans = Translation.objects.filter(respondent=paper.respondent, project=paper.project, column_name=cp.question.cid)
                    if trans:
                        if trans[0].content_en == '' or trans[0].content_en is not None:
                            content_en = trans[0].content_en
                            need_tran = False
                        else:
                            need_tran = True
                    else:
                        need_tran = True
                    if not showTran and not need_tran:
                        continue
                    
                    r = '%s%s' % (col_dict['paper_id'], startline)
                    excel.setRangeValBySheetIndex(1, r, paper.id)
                    r = '%s%s' % (col_dict['dealer_code'], startline)
                    excel.setRangeValBySheetIndex(1, r, paper.dealer.name)
                    r = '%s%s' % (col_dict['dealer_name_cn'], startline)
                    excel.setRangeValBySheetIndex(1, r, paper.dealer.name_cn)
                    r = '%s%s' % (col_dict['q_abbr'], startline)
                    excel.setRangeValBySheetIndex(1, r, cp.question.name_abbr)
                    r = '%s%s' % (col_dict['q_title'], startline)
                    excel.setRangeValBySheetIndex(1, r, cp.question.title)
                    r = '%s%s' % (col_dict['alt_title'], startline)
                    excel.setRangeValBySheetIndex(1, r, alt.title)
                    r = '%s%s' % (col_dict['alt_reason'], startline)
                    other_ans = ''
                    for alt in cp.question.alt_list:
                        if alt.cid == '98':
                            other_ans = ans_dict['%sother' % cp.question.cid]
                    reason = restore_result(cp.question, ans_dict['%s__open' % cp.question.cid], True, other98=other_ans)
                    if reason:
                        if reason.endswith('<br>'):
                            reason = reason[:-4]
                        if '<br>' in reason:
                            reason = reason.replace('<br>', '\n')
#                    for alt in cp.question.alt_list:
#                        if alt.cid == '98':
#                            #print cp.question.cid
#                            reason = '%s\n98.%s(%s)' % (reason, alt.title, ans_dict['%sother' % cp.question.cid])
                    excel.setRangeValBySheetIndex(1, r, reason)
                    if showTran:
                        r = 'H%s' % startline
                        excel.setRangeValBySheetIndex(1, r, content_en)
                    
                    startline += 1
        else:
            continue
    
    return startline, sh2_line

def gen_excel_open(excel, ans_dict, paper, sh2_line, showTran=False):
    need_tran, content_en = need_trans(paper, 'G50_A1')
    if  showTran or need_tran:
        write_base_info(excel, ans_dict, paper, sh2_line)
        r = '%s%s' % (col_dict['q_abbr'], sh2_line)
        excel.setRangeValBySheetIndex(2, r, 'G49a')
        r = '%s%s' % (col_dict['q_title'], sh2_line)
        excel.setRangeValBySheetIndex(2, r, u'做得比较好的地方')
        r = '%s%s' % (col_dict['alt_title'], sh2_line)
        excel.setRangeValBySheetIndex(2, r, ans_dict['G50__A1'])
        if showTran:
            r = 'G%s' % sh2_line
            excel.setRangeValBySheetIndex(2, r, content_en)
        sh2_line += 1
    
    need_tran, content_en = need_trans(paper, 'G50_A2')
    if showTran or need_tran:
        write_base_info(excel, ans_dict, paper, sh2_line)
        r = '%s%s' % (col_dict['q_abbr'], sh2_line)
        excel.setRangeValBySheetIndex(2, r, 'G49b')
        r = '%s%s' % (col_dict['q_title'], sh2_line)
        excel.setRangeValBySheetIndex(2, r, u'有待改进的地方 ')
        r = '%s%s' % (col_dict['alt_title'], sh2_line)
        excel.setRangeValBySheetIndex(2, r, ans_dict['G50__A2'])
        if showTran:
            r = 'G%s' % sh2_line
            excel.setRangeValBySheetIndex(2, r, content_en)
        sh2_line += 1
        
    
    if paper.project.id == 3:
        need_tran, content_en = need_trans(paper, 'T3')
        if  showTran or  need_tran:
            write_base_info(excel, ans_dict, paper, sh2_line)
            r = '%s%s' % (col_dict['q_abbr'], sh2_line)
            excel.setRangeValBySheetIndex(2, r, 'G50')
            r = '%s%s' % (col_dict['q_title'], sh2_line)
            excel.setRangeValBySheetIndex(2, r, u'总体看来,您对宝马4S店里的MINI售后专署接待区域感觉如何?（如适用于MINI授权的宝马经销店客户） ')
            r = '%s%s' % (col_dict['alt_title'], sh2_line)
            excel.setRangeValBySheetIndex(2, r, ans_dict['T3'])
            if showTran:
                r = 'G%s' % sh2_line
                excel.setRangeValBySheetIndex(2, r, content_en)
            sh2_line += 1
    return sh2_line

def need_trans(paper, column_name):
    need_tran = True
    trans = Translation.objects.filter(respondent=paper.respondent, project=paper.project, column_name=column_name)
    content_en = ''
    if trans:
        #print trans[0].content_en
        if trans[0].content_en != '' or trans[0].content_en is not None:
            content_en = trans[0].content_en
            need_tran = False
        else:
            need_tran = True
    else:
        need_tran = True
    
    return need_tran, content_en

def write_base_info(excel, ans_dict, paper, sh2_line):
    r = '%s%s' % (col_dict['paper_id'], sh2_line)
    excel.setRangeValBySheetIndex(2, r, paper.id)
    r = '%s%s' % (col_dict['dealer_code'], sh2_line)
    excel.setRangeValBySheetIndex(2, r, paper.dealer.name)
    r = '%s%s' % (col_dict['dealer_name_cn'], sh2_line)
    excel.setRangeValBySheetIndex(2, r, paper.dealer.name_cn)
    
def save_tran(term, transfile):
    #print 'translate file: %s' % transfile
    xlsfile = os.path.join(settings.RESOURCES_ROOT, transfile)
    book = xlrd.open_workbook(xlsfile)
    sh = book.sheet_by_index(0)
    #print sh.name, sh.nrows, sh.ncols
    for rx in range(2, sh.nrows):
        add_row(term, sh, rx)
    
    sh1 = book.sheet_by_index(1)
    #print sh1.name, sh1.nrows, sh1.ncols
    for rx in range(2, sh1.nrows):
        add_open_row(term, sh1, rx)
        
def add_row(term, sh, rx):
    texts = sh.row_values(rx)
    paper_id = int(texts[0])
    paper = _paper.get_paper(id=paper_id)
    dealer_code = texts[1]
    if isinstance(dealer_code, (int, long, float)):
        dealer_code = str(int(texts[1])).strip()
    if paper is None or paper.dealer.name != dealer_code:
        paper = _paper.get_paper(dealer__name=dealer_code, paper_type='BMW', status=enums.PAPER_STATUS_FINISH, term=term)
    if paper is None:
        print dealer_code, '==='
    name_abbr = texts[3]
    cp = CheckPoint.objects.get(name_abbr=name_abbr, project=paper.project)
    tran = texts[7]
    if hasattr(tran, 'strip'):
        tran = tran.strip()
        
    saveQuestionTrans(paper, tran, cp.name)
    diffs = PaperDiff.objects.filter(final_paper=paper)
    if diffs and len(diffs) > 0:
        saveQuestionTrans(diffs[0].fw_paper, tran, cp.name)

def add_open_row(term, sh, rx):
    texts = sh.row_values(rx)
    paper_id = int(texts[0])
    paper = _paper.get_paper(id=paper_id)
    dealer_code = texts[1]
    if isinstance(dealer_code, (int, long, float)):
        dealer_code = str(int(texts[1])).strip()
    if paper is None or paper.dealer.name != dealer_code:
        paper = _paper.get_paper(dealer__name=dealer_code, paper_type='BMW', status=enums.PAPER_STATUS_FINISH, term=term)
    name_abbr = texts[3]
    tran = texts[6]
    if hasattr(tran, 'strip'):
        tran = tran.strip()
    
    if name_abbr == 'G49a':
        col_name = 'G50_A1'
    if name_abbr == 'G49b':
        col_name = 'G50_A2'
    if name_abbr == 'G50':
        col_name = 'T3'
        
    saveQuestionTrans(paper, tran, col_name)
    
    diffs = PaperDiff.objects.filter(final_paper=paper)
    if diffs and len(diffs) > 0:
        saveQuestionTrans(diffs[0].fw_paper, tran, col_name)
    
def saveQuestionTrans(paper, tran, col_name):
    if paper and tran:
        t, create = Translation.objects.get_or_create(respondent=paper.respondent, project=paper.project, column_name=col_name)
        t.content_en = tran
        t.save()
        #print  paper.id, paper.paper_type, paper.dealer.name, t.column_name, tran
    
class Item(object):
    pass
        
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'need method(input/output)!'
        sys.exit(1)
    term = _term.get_cur_input_term()
    print term.name_cn
    if sys.argv[1] == 'input':
#        save_tran(term, 'tran0407.xls')
#        save_tran(term, 'tran0411.xls')
#        save_tran(term, 'tran0411_v2.xls')
#        save_tran(term, 'tran0411_v3.xls')
#        save_tran(term, 'tran0412-2.xls')
        #save_tran(term, 'tran0414.xls')
        #save_tran(term, 'tran0415.xls')
        #save_tran(term, u'tran-all_v1_0405.xls')
        #save_tran(term, u'tran-all_0415_final.xls')
        #save_tran(term, u'tran0419.xls')
#        save_tran(term, u'2012年第2期_tran_all_120630170929.xls')
#        save_tran(term, u'2012年第3期_tran_0920.xls')
#        save_tran(term, u'2012年第3期_tran_need_120920212434.xls')
#        save_tran(term, u'2012年第3期_tran_0921.xls')
        save_tran(term, u'2012年第3期_tran_need_0921.xls')
        
    if sys.argv[1] == 'output':
        write_data(term, False)
