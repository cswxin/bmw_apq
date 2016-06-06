#encoding:utf-8
'''
Created on 2012-6-7

@author: junhua
'''
import os, sys
sys.path.insert(0, os.path.abspath(os.curdir))
import time
import copy
import settings
import constant
from mc import enums
from mc.models import Report
from mcview.chart_utils import get_ave_score
from service.easyExcel import easyExcel
from service.core import _paper, _dealer, _term, _project, _checkpoint, _report

def gen_dealer_hnf_report(term_id):
    source_file_name = u'hnf/dealer_hnf.xls'
    source_file_name = os.path.join(settings.RESOURCES_ROOT, source_file_name)
    dealertypes = _dealer.get_dealer_types()
    term_list = map(copy.copy, _term.get_all_terms().filter(id__lte=term_id))
    excel = easyExcel(source_file_name)
    try:
        sheet = 'sheet1'
        for dt in dealertypes:
            project_id = constant.dealertype_id_to_project_id(dt.id)
            project = _project.get_project_by_id(project_id)
            papers = _paper.get_papers_by_term_project_Dealer(term_id, project_id, dt.id)
            for index, paper in enumerate(papers):
                term = paper.term
                dealer = paper.dealer
                filename = u'%s_%s_%s_历史现在未来报告.xls' % (term.name, dealer.name_cn, dealer.name)
                target_file_name = os.path.join(settings.MEDIA_ROOT, 'hnf_report', filename)
                if paper.visit_end and paper.visit_begin:
                    paper.visit_minutes = (paper.visit_end - paper.visit_begin).seconds / 60
                else:
                    paper.visit_minutes = 0
                excel.setSheetName(sheet, u'%s历史现在未来报告' % dealer.name_cn)
                sheet = u'%s历史现在未来报告' % dealer.name_cn
                data_sheet = 'datasheet'
                excel.setRangeVal(data_sheet, 'B2', dealer.name_cn)
                excel.setRangeVal(data_sheet, 'B3', dealer.name_en)
                excel.setRangeVal(data_sheet, 'E2', dealer.name)
                excel.setRangeVal(data_sheet, 'H2', dealer.city_cn)
                excel.setRangeVal(data_sheet, 'H3', dealer.city_en)
                excel.setRangeVal(data_sheet, 'K2', dealer.province_cn)
                excel.setRangeVal(data_sheet, 'K3', dealer.province_en)
                excel.setRangeVal(data_sheet, 'N2', dealer.region.name_cn)
                excel.setRangeVal(data_sheet, 'N3', dealer.region.name_en)
                excel.setRangeVal(data_sheet, 'P2', u'本期总得分（%s）：' % term.name_cn)
                excel.setRangeVal(data_sheet, 'P3', u'Overall score of %s wave' % term.name_en)
                excel.setRangeVal(data_sheet, 'Q2', round(paper.score, 1))
                excel.setRangeVal(data_sheet, 'T2', paper.visit_begin)
                excel.setRangeVal(data_sheet, 'W2', paper.visit_end)
                excel.setRangeVal(data_sheet, 'Z2', paper.visit_minutes)
                
                insert_paper_data(excel, data_sheet, term_list, project, dealer, dealer.dealertype, paper.paper_type)
                
                excel.save(target_file_name)
    finally:
        excel.close()
            

def gen_region_hnf_report(term_id):
    source_file_name = u'hnf/region_hnf.xls'
    source_file_name = os.path.join(settings.RESOURCES_ROOT, source_file_name)
    excel = easyExcel(source_file_name)
    term_list = map(copy.copy, _term.get_all_terms().filter(id__lte=term_id))
    #除去品牌的report,采用全国的数据
    reports = Report.objects.filter(term__id=term_id, dealer__has_child=True).exclude(score=None).exclude(dealer__level=7)
    kind_dict = constant.data_compare_kind_dict
    kind_dict = dict(zip(kind_dict.values(), kind_dict.keys()))
    try:
        sheet = 'sheet1'
        for index, report in enumerate(reports):
            term = report.term
            dealer = report.dealer
            dealertype = report.dealertype
            project = report.project
            paper_type = report.paper_type
            level = 7 #全国没有对比，做为品牌对比
            if report.dealer.level != 0:
                level = report.dealer.level
            kind = kind_dict[level]
            item_name = constant.data_compare_dict[kind]
            item_name_en = constant.data_compare_en_dict[kind]
            filename = u'%s_%s_%s_%s_历史现在未来报告.xls' % (item_name, term.name, dealer.name_cn, dealertype.name_cn)
            target_file_name = os.path.join(settings.MEDIA_ROOT, 'hnf_report', filename)
            excel.setSheetName(sheet, u'%s历史现在未来报告' % item_name)
            sheet = u'%s历史现在未来报告' % item_name
            ans = u'2012年%s售后服务评估结果    %s After-sales Service Evaluation Result' % (item_name, item_name_en)
            excel.setRangeVal(sheet, 'A1', ans)
            data_sheet = 'datasheet'
            ans = u'%s数据对比和历史/现在/未来 %s Data Comparison And History/Current/Future' % (item_name, item_name_en)
            excel.setRangeVal(data_sheet, 'A1', ans)
            ans = u'%s名称：' % item_name
            excel.setRangeVal(data_sheet, 'A2', ans)
            excel.setRangeVal(data_sheet, 'A3', item_name_en)
            ans = dealer.name_cn
            if level == 0:
                ans = dealertype.name_cn
            excel.setRangeVal(data_sheet, 'B2', ans)
            ans = dealer.name_en
            if level == 0:
                ans = dealertype.name_en
            excel.setRangeVal(data_sheet, 'B3', ans)
            excel.setRangeVal(data_sheet, 'D2', u'本期总得分（%s）：' % term.name_cn)
            excel.setRangeVal(data_sheet, 'D3', u'Overall score of %s wave' % term.name_en)
            excel.setRangeVal(data_sheet, 'E2', round(report.score, 1))
            
            insert_paper_data(excel, data_sheet, term_list, project, dealer, dealertype, paper_type)
            
            excel.save(target_file_name)
            
    finally:
        excel.close()

cp_nameabbr_row_dict = {'Total':6,
                        'A':11, 'A1':16, 'A2':21, 'A3':26, 'A4':31, 'A5':36, 'A6':41, 'A7':46,
                        'B':50, 'B8':55, 'B9':60, 'B10':65, 'B11':70, 'B12':75, 'B13':80, 'B14':85, 'B15':90, 'B16':95, 'B17':100, 'B18':105, 'B19':110, 'B20':115, 'B21':120, 'B22':125, 'B23':130, 'B24':135,
                        'C':139, 'C25':144, 'C26':149, 'C27':154, 'C28':159, 'C29':164,
                        'D':168, 'D30':173, 'D31':178, 'D32':183, 'D33':188, 'D34':193, 'D35':198, 'D36':203, 'D37':208, 'D38':213, 'D39':218, 'D40':223, 'D41':228, 'D42':233,
                        'E':237, 'E43':242, 'E44':247, 'E45':252, 'E46':257,
                        'F':261, 'F47':266, 'F48':271}
def insert_paper_data(excel, sheet, term_list, project, dealer, dealertype, paper_type):
    paper_type = enums.BMW_PAPER_TYPE
    for term in term_list:
        tmp_project_id = project.id
        if term.id <= 4:
            tmp_project_id = 1
            paper_type = enums.FW_PAPER_TYPE
        else:
            paper_type = enums.BMW_PAPER_TYPE
            if tmp_project_id == constant.competition_project_id:
                paper_type = enums.FW_PAPER_TYPE
        protmp = _project.get_project_id_map()[tmp_project_id]
        cp_name_list = _checkpoint.get_project_cp_name_list_with_total(protmp)
        score_list_dealer = _report.get_dealer_score(term, dealer, protmp, dealertype, paper_type, cp_name_list)
        score_dict_dealer = {}
        for i, cp_name in enumerate(cp_name_list):
            if score_list_dealer:
                score_dict_dealer[cp_name] = score_list_dealer[i]
        term.score_dict_dealer = score_dict_dealer
    
    cp_group_list = map(copy.copy, _checkpoint.get_project_cp_list_with_total(project))
    for i, cp_group in enumerate(cp_group_list):
        if 'G' in cp_group.name_abbr:
            continue
            
        W1_list = []
        W2_list = []
        W3_list = []
        W4_list = []
        
        cur_term = term_list[-1]
        for tid in range(cur_term.id):
            w = tid % 4
            if w == 0:
                if term_list[tid]:
                    if term_list[tid].score_dict_dealer:
                        try:
                            W1_list.append(term_list[tid].score_dict_dealer[cp_group.name])
                        except:
                            W1_list.append(-1)
                    else:
                        W1_list.append(-1)
            elif w == 1:
                if term_list[tid]:
                    if term_list[tid].score_dict_dealer:
                        try:
                            W2_list.append(term_list[tid].score_dict_dealer[cp_group.name])
                        except:
                            W2_list.append(-1)
                    else:
                        W2_list.append(-1)
            elif w == 2:
                if term_list[tid]:
                    if term_list[tid].score_dict_dealer:
                        try:
                            W3_list.append(term_list[tid].score_dict_dealer[cp_group.name])
                        except:
                            W3_list.append(-1)
                    else:
                        W3_list.append(-1)
            elif w == 3:
                if term_list[tid]:
                    if term_list[tid].score_dict_dealer:
                        try:
                            W4_list.append(term_list[tid].score_dict_dealer[cp_group.name])
                        except:
                            W4_list.append(-1)
                    else:
                        W4_list.append(-1)
            else:
                pass
        
        series_list = []
        series_list.append(dict(name=u'W1', value=W1_list))
        series_list.append(dict(name=u'W2', value=W2_list))
        series_list.append(dict(name=u'W3', value=W3_list))
        series_list.append(dict(name=u'W4', value=W4_list))
        
        fill_cp_data(excel, sheet, cp_group, series_list)

def fill_cp_data(excel, sheet, cp, series_list):
    if cp.name_abbr not in cp_nameabbr_row_dict.keys():
        return
    top3, ytd, ave, future_score, point = get_ave_score(series_list)
    row = cp_nameabbr_row_dict[cp.name_abbr]
    for index, series in enumerate(series_list):
        values = series['value']
        if len(values) == 1:
            values.append(future_score)
        ans = values[0]
        col = get_char(index)
        if ans != -1:
            excel.setRangeVal(sheet, '%s%s' % (col, row), ans)
        ans = values[1]
        col = get_char(index + 5)
        if ans != -1:
            excel.setRangeVal(sheet, '%s%s' % (col, row), ans)
    if top3[1] != -1:
        excel.setRangeVal(sheet, 'J%s' % row, top3[1])
    if ytd[1] != -1:
        excel.setRangeVal(sheet, 'K%s' % row, ytd[1])
    if ave[1] != -1:
        excel.setRangeVal(sheet, 'L%s' % row, ave[1])
        
START_COL_NUM = ord('a')
char_list = []
def gen_char_list(index, need_empty=False):
    #index从0开始
    global char_list
    if need_empty:
        char_list = []
    if index < 26:
        char_list.append(chr(index + START_COL_NUM))
    else:
        temp = index / 26 - 1
        char_list.append(chr(index % 26 + START_COL_NUM))
        gen_char_list(temp)
        
def get_char(index):
    gen_char_list(index, need_empty=True)
    char_list.reverse()
    return ''.join(char_list)

if __name__ == '__main__':
    term_id = 5
    t1 = time.clock()
    print 
    gen_dealer_hnf_report(term_id)
    t2 = time.clock()
    print t2 - t1
    gen_region_hnf_report(term_id)
    t3 = time.clock()
    print t3 - t2
    print 'total', t3 - t1
