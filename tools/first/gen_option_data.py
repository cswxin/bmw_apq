#encoding:utf-8
'''
Created on 2012-5-18

@author: junhua
'''
import os, sys

sys.path.insert(0, os.path.abspath(os.curdir))
from django.conf import settings

from service.core import _project, _term
from service.core import _checkpoint
from service.core import _question
from service.core import _paper
from service.easyExcel import easyExcel

from mc import enums
from mc.models import PaperAudit
from survey.models import Question, Alternative
from survey.survey_utils import get_respondentdata_dict_by_paper

START_COL_NUM = ord('a')
END_COL_NUM = ord('z')
COL_DICT = {} #{'qid_21':'a','qid_22':'b',...,'qid_21':'aa'}

columns = [u'经销商代码', u'经销商名称', u'问卷id', u'客户姓名', u'客人联系方式', u'进店人数', u'评估员姓名', u'总得分',
           u'电话预约时间', u'访问时间', u'进店时间', u'出店时间', u'预计完工日期', u'预计完工时间', u'最终完工日期', u'最终完工时间', u'接受售后服务类型', u'车型', u'排挡方式', u'服务顾问姓名', u'服务顾问性别',
           u'QC一审', u'QC二审', u'QC三审']        


def make_excel(term_id):
    term = _term.get_term_by_id(term_id)
    target_file = os.path.join(settings.RESOURCES_ROOT, u'data/%s_option_data.xls' % term.name_cn)
    #默认保存2007的格式，需手动转换
    
    projects = _project.get_2012_projects()
    
    excel = easyExcel()
    try:
        for index, project in enumerate(projects):
            sheetname = project.name
            excel.setSheetName('sheet%d' % (index + 1), sheetname)
            gen_col_dict(project, excel, sheetname)
            papers = _paper.get_papers(project=project, paper_type=enums.FW_PAPER_TYPE, term=term)
            for i, paper in enumerate(papers):
                print paper.id
                ans_dict = get_respondentdata_dict_by_paper(paper)
                dealername = ''
                dealername_cn = ''
                dealer = paper.dealer
                if dealer:
                    dealername = paper.dealer.name
                    dealername_cn = paper.dealer.name_cn
#                print paper.id, paper.survey_code, dealername, dealername_cn
                cellrow = i + 2
                excel.setRangeVal(sheetname, '%s%s' % (get_char(0), cellrow), dealername)
                excel.setRangeVal(sheetname, '%s%s' % (get_char(1), cellrow), dealername_cn)
                excel.setRangeVal(sheetname, '%s%s' % (get_char(2), cellrow), paper.id)
                
                excel.setRangeVal(sheetname, '%s%s' % (get_char(3), cellrow), ans_dict['customer_name'])#
                excel.setRangeVal(sheetname, '%s%s' % (get_char(4), cellrow), ans_dict['customer_address'])
                excel.setRangeVal(sheetname, '%s%s' % (get_char(5), cellrow), paper.visitor_num)
                excel.setRangeVal(sheetname, '%s%s' % (get_char(6), cellrow), ans_dict['appraiser_code'])
                excel.setRangeVal(sheetname, '%s%s' % (get_char(7), cellrow), '%.2f' % paper.score)
                excel.setRangeVal(sheetname, '%s%s' % (get_char(8), cellrow), ans_dict['booking_date'])
                excel.setRangeVal(sheetname, '%s%s' % (get_char(9), cellrow), ans_dict['visit_date'])
                excel.setRangeVal(sheetname, '%s%s' % (get_char(10), cellrow), ans_dict['visit_begin_time'])
                excel.setRangeVal(sheetname, '%s%s' % (get_char(11), cellrow), ans_dict['visit_end_time'])
                excel.setRangeVal(sheetname, '%s%s' % (get_char(12), cellrow), ans_dict['estimate_finish_date'])
                excel.setRangeVal(sheetname, '%s%s' % (get_char(13), cellrow), ans_dict['estimate_finish_time'])
                excel.setRangeVal(sheetname, '%s%s' % (get_char(14), cellrow), ans_dict['repare_finish_date'])
                excel.setRangeVal(sheetname, '%s%s' % (get_char(15), cellrow), ans_dict['repare_finish_time'])
                base_ans = ans_dict['service_type']
                alt = Alternative.objects.get(id=base_ans)
                excel.setRangeVal(sheetname, '%s%s' % (get_char(16), cellrow), alt.title)
                
                base_ans = ans_dict['car_type']
                alt = Alternative.objects.get(id=base_ans)
                cartypes = alt.title
                car_type__open = ans_dict['car_type__open']
                if car_type__open:
                    cartypes = '%s %s' % (cartypes, car_type__open)
                excel.setRangeVal(sheetname, '%s%s' % (get_char(17), cellrow), cartypes)
                
                base_ans = ans_dict['at_mt']
                alt = Alternative.objects.get(id=base_ans)
                excel.setRangeVal(sheetname, '%s%s' % (get_char(18), cellrow), alt.title)
                excel.setRangeVal(sheetname, '%s%s' % (get_char(19), cellrow), ans_dict['consultant_name'])
                
                base_ans = ans_dict['consultant_sex']
                alt = Alternative.objects.get(id=base_ans)
                excel.setRangeVal(sheetname, '%s%s' % (get_char(20), cellrow), alt.title)
                qc1 = PaperAudit.objects.filter(paper=paper, new_status=enums.FW_PAPER_STATUS_WAIT_AUDIT_2)
                if qc1:
                    excel.setRangeVal(sheetname, '%s%s' % (get_char(21), cellrow), qc1[0].user.username)
                qc2 = PaperAudit.objects.filter(paper=paper, new_status=enums.FW_PAPER_STATUS_WAIT_AUDIT_3)
                if qc2:
                    excel.setRangeVal(sheetname, '%s%s' % (get_char(22), cellrow), qc2[0].user.username)
                qc3 = PaperAudit.objects.filter(paper=paper, new_status=enums.FW_PAPER_STATUS_WAIT_AUDIT_4)
                if qc3:
                    excel.setRangeVal(sheetname, '%s%s' % (get_char(23), cellrow), qc3[0].user.username)
            
                for key in COL_DICT.keys():
                    if '_' not in key:
                        qid = key
                        qcid = Question.objects.get(id=qid).cid
                        base_ans = ans_dict[qcid]
                        if base_ans is None:
                            continue
                        #print paper.id ,qid, base_ans
                        alt = Alternative.objects.get(id=base_ans)
                        cell = '%s%s' % (COL_DICT[qid], i + 2)
                        if u'是' in alt.title:
                            excel.setRangeVal(sheetname, cell, u'是')
                        else:
                            excel.setRangeVal(sheetname, cell, alt.title)
                        continue
                    keys = key.split('_')
                    qid = keys[0]
                    ans_cid = keys[1]
#                    if 'A' in ans_cid:
#                        if '1' not in ans_cid:
#                            continue
                    qcid = Question.objects.get(id=qid).cid
                    qkey = '%s__open' % qcid
                    base_ans = ans_dict[qcid]
                    if base_ans is None:
                        continue
                    #print paper.id ,qid, base_ans
                    alt = Alternative.objects.get(id=base_ans)
#                    cell = '%s%s' % (COL_DICT[key], i + 2)
#                    if 'A' in ans_cid:
#                        if u'是' in alt.title:
#                            excel.setRangeVal(sheetname, cell, u'是')
#                        else:
#                            excel.setRangeVal(sheetname, cell, alt.title)
                    if u'否' not in alt.title:
                        continue
                    #print paper.id, ans_dict
                    ans = ans_dict[qkey]
                    ans_list = []
                    if not ans:
                        continue
                    if '^-^' in ans:
                        ans_list = ans.split('^-^')
                    if ans_list:
                        for a in ans_list:
                            cell = '%s%s' % (COL_DICT[key], i + 2)
                            try:
                                alt_cid = int(a)
                                if int(ans_cid) == alt_cid:
                                    excel.setRangeVal(sheetname, cell, alt_cid)
                            except:
                                if ans_cid == 'open':
                                    excel.setRangeVal(sheetname, cell, a)
        excel.save(target_file)
    finally:
        excel.close()
    return target_file

def gen_col_dict(project, excel, sheetname):
    global COL_DICT
    COL_DICT = {}
    col_index = 0
    for index, coltitle in enumerate(columns):
        col_index = index
        cell = get_char(col_index)
        excel.setRangeVal(sheetname, '%s1' % cell, coltitle)
    
    cp_list = _checkpoint.get_project_sub_cp_list(project).filter(question__questiontype=2)
    col_index = len(columns)
    for cp in cp_list:
        #alt_list = _question.get_alt_list_exclude_a(cp.question)
        alt_list = cp.question.alt_list
        cell = get_char(col_index)
        COL_DICT['%s' % cp.question.id] = cell
        excel.setRangeVal(sheetname, '%s1' % cell, '%s' % cp.question.name_abbr)
        col_index += 1
        alt_list = alt_list.exclude(cid__icontains='a').order_by('cid')
        if alt_list:
            for alt in alt_list:
                cell = get_char(col_index)
                COL_DICT['%s_%s' % (cp.question.id, alt.cid)] = cell
                excel.setRangeVal(sheetname, '%s1' % cell, '%s_%s' % (cp.question.name_abbr, alt.cid))
                col_index += 1
            cell = get_char(col_index)
            COL_DICT['%s_open' % cp.question.id] = cell
            excel.setRangeVal(sheetname, '%s1' % cell, '%s_open' % cp.question.name_abbr)
            col_index += 1

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
    make_excel(5)
    make_excel(6)
    make_excel(7)
    make_excel(8)
#    for i in range(27 * 26 + 1):
#        print get_char(i),
