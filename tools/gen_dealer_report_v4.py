#encoding:utf-8

"""
jdpa_car dealer report生成
"""

import os, sys
sys.path.insert(0, os.path.abspath(os.curdir))
from django.conf import settings
from django.db.transaction import commit_on_success
from mc.models import Term, Dealer, Report
from survey.models import Project
import xlrd
import win32com.client as win32
import shutil
import MyDbUtils
import cStringIO
import cPickle as pickle

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

#复制模板
def copy_excel(source_file_name, target_file_name):
    xlsfile = source_file_name
    dsfile = os.path.join(settings.MEDIA_ROOT, target_file_name)
    shutil.copyfile(xlsfile, dsfile)
    return

#填写EXCEL数据
def get_file(filename):
    x1 = win32.Dispatch('Excel.Application')
    x1.DisplayAlerts = False
    filename = filename.replace('/', '\\')
    ss = x1.Workbooks.Open(filename)
    return ss, x1

def close_file(ss, x1):
    ss.Save()
    ss.Close()
    x1.Application.Quit()

def get_file_data(filename):
    filename = filename.replace('/', '\\')
    book = xlrd.open_workbook(filename)
    return book


#写入答案
def set_answers(cell, sh, ans):
    try:
        sh.Range(cell).Value = ans
    except:
        print 'error-----', cell, ans
        
def get_dealer_score(project, term, dealer):
    reports = Report.objects.filter(project=project, term=term, dealer=dealer)
    score = ''
    if reports:
        report = reports[0]
        score = report.score
    return score

def get_sql_info(sql):
    c, con = MyDbUtils.cursor()
    try:
        c.execute(sql)
        data_dict = c.fetchall()[0]
    except Exception, e:
        data_dict = {}
        print e
    finally:
        if c:
            c.close()
        if con:
            con.commit()
            con.close()
        return data_dict

def get_score(data_dict, qid):
    score = data_dict.get(qid)
    if score == -999:
        score = '/'
    return score

def write_sheet_3(data_sheet3, score_dict_dealer, score_dict_region, score_dict_nation, answer_dict_dealer):
    answer_row_dict = {
                        'Q1':19,
                        'Q2':21,
                        'Q4a':23,
                        'Q4b':25,
                        'Q4c':27,
                        'Q4d':29,
                        'Q4e':31,
                        'Q5':33,
                        'Q6':35,
                        'Q8a':37,
                        'Q8b':39,
                        
                        'Q9a':44,
                        'Q9b':46,
                        'Q10':48,
                        'Q11a':50,
                        'Q11b':52,
                        'Q14':54,
                        'Q15':56,
                        'Q16a':58,
                        'Q16b':60,
                        'Q16c':62,
                        'Q16d':64,
                        'Q17':66,
                        'Q18':68,
                        'Q19':70,
                        'Q20':72,
                        'Q22':74,
                        'Q23':76,
                        'Q24':78,
                        'Q25':80,
                        'Q26':82,
                        'Q27':84,
                        'Q28':86,
                        'Q29':88,
                        'Q30':90,
                        'Q31':92,
                        'Q32':94,
                        'Q33':96,
                        
                        'Q35a':101,
                        'Q35b':103,
                        'Q35c':105,
                        'Q36':107,
                        'Q37':109,
                        'Q38':111,
                        'Q39':113,
                        'Q40':115,
                        'Q41':117,
                        'Q42':119,
                        'Q43a':121,
                        'Q43b':123,
                        'Q43c':125,
                        
                        'Q45':130,
                        'Q46a':132,
                        'Q46b':134,
                        'Q48':136,
                        'Q50':138,
                        'Q51':140,
                        'Q52':142,
                        'Q53':144,
                        
                        'Q55':149,
                        'Q58':151,
                        'Q59':153,
                        
                        'Q65':158,
                        'Q66':160,
                        'Q67':162,
                        'Q68':164,
                        }
    
    score_row_dict = {
                        'Q1':19,
                        'Q2':21,
                        'Q4':23,
                        'Q5':33,
                        'Q6':35,
                        'Q8':37,
                        
                        'Q9':44,
                        'Q10':48,
                        'Q11':50,
                        'Q14':54,
                        'Q15':56,
                        'Q16':58,
                        'Q17':66,
                        'Q18':68,
                        'Q19':70,
                        'Q20':72,
                        'Q22':74,
                        'Q23':76,
                        'Q24':78,
                        'Q25':80,
                        'Q26':82,
                        'Q27':84,
                        'Q28':86,
                        'Q29':88,
                        'Q30':90,
                        'Q31':92,
                        'Q32':94,
                        'Q33':96,
                        
                        'Q35':101,
                        'Q36':107,
                        'Q37':109,
                        'Q38':111,
                        'Q39':113,
                        'Q40':115,
                        'Q41':117,
                        'Q42':119,
                        'Q43':121,
                        
                        'Q45':130,
                        'Q46':132,
                        'Q48':136,
                        'Q50':138,
                        'Q51':140,
                        'Q52':142,
                        'Q53':144,
                        
                        'Q55':149,
                        'Q58':151,
                        'Q59':153,
                        
                        'Q65':158,
                        'Q66':160,
                        'Q67':162,
                        'Q68':164,
                        }
    for (qid, row) in answer_row_dict.items():
        set_answers("Q%s" % row, data_sheet3, answer_dict_dealer.get(qid))
        
    for (qid, row) in score_row_dict.items():    
        set_answers("R%s" % row, data_sheet3, get_score(score_dict_dealer, qid))
        set_answers("S%s" % row, data_sheet3, get_score(score_dict_region, qid))
        set_answers("T%s" % row, data_sheet3, get_score(score_dict_nation, qid))

def write_sheet_4(data_sheet4, score_dict_dealer, score_dict_region, score_dict_nation, answer_dict_dealer):
    answer_row_dict = {
                        'Q3':19,
                        'Q7a':21,
                        'Q7b':23,
                        
                        'Q12a':31,
                        'Q12b':33,
                        'Q12c':35,
                        'Q12d':37,
                        'Q12e':39,
                        'Q12f':41,
                        'Q12g':43,
                        'Q12h':45,
                        'Q12i':47,
                        'Q13a':49,
                        'Q13b':51,
                        'Q13c':53,
                        'Q13d':55,
                        'Q21':57,
                        'Q34a':59,
                        'Q34b':61,
                        
                        'Q44a':69,
                        'Q44b':71,
                        
                        'Q47':79,
                        'Q49':81,
                        'Q54':83,
                        
                        'Q56':88,
                        'Q57':90,
                        'Q60':92,
                        
                        'Q61':97,
                         }
    answer_row_dict2 = {
                        'Q7c':27,
                        'Q34c':65,
                        'Q44c':75,
                        'Q62':101,
                        'Q63':104,
                        'Q64':107,
                          }
    score_row_dict = {
                        'Q3':19,
                        'Q7':21,
                        
                        'Q12':31,
                        'Q13':49,
                        'Q21':57,
                        'Q34':59,
                        
                        'Q44':69,
                        
                        'Q47':79,
                        'Q49':81,
                        'Q54':83,
                        
                        'Q56':88,
                        'Q57':90,
                        'Q60':92,
                        
                        'Q61':97,
                         }
    for (qid, row) in answer_row_dict.items():
        set_answers("Q%s" % row, data_sheet4, answer_dict_dealer.get(qid))
        
    for (qid, row) in answer_row_dict2.items():
        set_answers("C%s" % row, data_sheet4, answer_dict_dealer.get(qid))
        
    for (qid, row) in score_row_dict.items():    
        set_answers("R%s" % row, data_sheet4, get_score(score_dict_dealer, qid))
        set_answers("S%s" % row, data_sheet4, get_score(score_dict_region, qid))
        set_answers("T%s" % row, data_sheet4, get_score(score_dict_nation, qid))

def gen_top3(term_list, dealer):
    top3 = '-'
    score_list = [ ]
    for t in term_list:
        reports = Report.objects.filter(term=t, dealer=dealer)
        if not reports:
            continue
        score = reports[0].score
        if score == -1:
            continue
        score_list.append(score)
    total = 0.0
    top3_total = 0.0
    count = len(score_list)
    for score in score_list:
        if score == -1:
            count -= 1
            continue
        total += score
    if count == 4:
        score_list.sort()
        top3_total = total - score_list[0]
        top3 = top3_total / 3
    else:
        top3_total = total
        if count <= 0:
            top3 = '-'
        else:
            top3 = top3_total / count
    return top3

#ycf new 4个季度平均分
def gen_avg4(term_list, dealer):
    avg4 = '-'
    score_list = [ ]
    for t in term_list:
        reports = Report.objects.filter(term=t, dealer=dealer)
        if not reports:
            continue
        score = reports[0].score
        if score == -1:
            continue
        score_list.append(score)
    total = 0.0
    top4_total = 0.0
    count = len(score_list)
    for score in score_list:
        if score == -1:
            count -= 1
            continue
        total += score
    top4_total = total
    if count <= 0:
            avg4 = '-'
    else:
            avg4 = top4_total / count
    return avg4
#    if count == 4:
#        score_list.sort()
#        top3_total = total - score_list[0]
#        top3 = top3_total / 3
#    else:
#        top3_total = total
#        if count <= 0:
#            top3 = '-'
#        else:
#            top3 = top3_total / count
#    return top3    
#生成dealer_report
def gen_dealer_report(project, term, term1, term2, term3):
    if project.id == 1:
        source_file_name = u'doc/templates/APQ 2014 Wave IV_templet_BMW_20141212.xls'
    if project.id == 2:
        source_file_name = u'doc/templates/APQ 2014 Wave IV_templet_MINI_20141212.xls'
    
    source_file_name = os.path.join(settings.SITE_ROOT, source_file_name)
    
    #全国分数
    dealer_naiton = Dealer.objects.get(name=u'全国')
    report_nation_t1 = Report.objects.get(project=project, term=term1, dealer=dealer_naiton)
    report_nation_t2 = Report.objects.get(project=project, term=term2, dealer=dealer_naiton)
    report_nation_t3 = Report.objects.get(project=project, term=term3, dealer=dealer_naiton)
    report_nation = Report.objects.get(project=project, term=term, dealer=dealer_naiton)
    
    score_nation = report_nation.score
    
    report_list = Report.objects.filter(project=project, term=term, dealer__has_child=False).order_by('-score')
    report_max_nation = report_list[0]
    for report in report_list:
        dealer = report.dealer
#        if dealer.name !=u'30736':
#            continue

#        if dealer.name not in ['37129','33963','28641','28778']:
#            continue
        
        import pythoncom
        pythoncom.CoInitialize()
        target_file_name = u'report/%s/%s/%s/%s/%s_%s_%s_%s_报告.xls' % (term.id, dealer.dealertype.name_cn, dealer.parent.parent.name_cn, dealer.province_cn, dealer.name, dealer.dealertype.name_cn, dealer.abbr_cn, term.name)
        dsfile = os.path.join(settings.MEDIA_ROOT, target_file_name)
        
#        if not os.path.exists(dsfile):
#        print dealer.name,dealer.dealertype.name_cn
        gen_report(term1, term2, term3, dealer_naiton, dealer, source_file_name, target_file_name, report_nation, report_nation_t1, report_nation_t2, report_nation_t3, score_nation, project, term, report, report_max_nation)
        #pythoncom.CoUninitialize()
    return

@commit_on_success
def gen_report(term1, term2, term3, dealer_naiton, dealer, source_file_name, target_file_name, report_nation, report_nation_t1, report_nation_t2, report_nation_t3, score_nation, project, term, report, report_max_nation):
    term_dir = os.path.join(settings.MEDIA_ROOT, 'report/%s' % term.id)
    if not os.path.exists(term_dir):
        os.mkdir(term_dir)
    dealertype_dir = os.path.join(term_dir, dealer.dealertype.name_cn)
    if not os.path.exists(dealertype_dir):
        os.mkdir(dealertype_dir)    
    region_dir = os.path.join(dealertype_dir, dealer.parent.parent.name_cn)
    if not os.path.exists(region_dir):
        os.mkdir(region_dir)
    province_dir = os.path.join(region_dir, dealer.province_cn)
    if not os.path.exists(province_dir):
        os.mkdir(province_dir)
        
    copy_excel(source_file_name, target_file_name)
    
    #获得新文件操作权
    filename = os.path.join(settings.MEDIA_ROOT, target_file_name)
    ss, x1 = get_file(filename)
    try:
        report_max_region = None
        report_region_list = Report.objects.filter(project=project, term=term, dealer__parent__parent=dealer.parent.parent).order_by('-score')
        if report_region_list:
            report_max_region = report_region_list[0]
        
        report_t1 = None
        report_t1_list = Report.objects.filter(project=project, term=term1, dealer=dealer)
        if report_t1_list:
            report_t1 = report_t1_list[0]
        
        report_t2 = None
        report_t2_list = Report.objects.filter(project=project, term=term2, dealer=dealer)
        if report_t2_list:
            report_t2 = report_t2_list[0]
        
        report_t3 = None
        report_t3_list = Report.objects.filter(project=project, term=term3, dealer=dealer)
        if report_t3_list:
            report_t3 = report_t3_list[0]
            
        #sheet1
        data_sheet1 = ss.Sheets(1)
        set_answers("B31", data_sheet1, dealer.abbr_cn)
        set_answers("B32", data_sheet1, dealer.abbr_en)
        
        #sheet5
        data_sheet5 = ss.Sheets(5)
        #基本信息
        set_answers("B1", data_sheet5, dealer.name_cn)
        set_answers("C1", data_sheet5, dealer.name_en)
        set_answers("B2", data_sheet5, dealer.name)
        set_answers("B3", data_sheet5, dealer.city_cn)
        set_answers("C3", data_sheet5, dealer.city_en)
        set_answers("B4", data_sheet5, dealer.province_cn)
        set_answers("C4", data_sheet5, dealer.province_en)
        set_answers("B5", data_sheet5, dealer.parent.parent.name_cn)
        set_answers("C5", data_sheet5, dealer.parent.parent.name_en)
        set_answers("B6", data_sheet5, report.score)
        set_answers("D6", data_sheet5, report.part_a)
        set_answers("F6", data_sheet5, report.part_b)
        
        #年度Top3成绩平均得分
#        term_list = Term.objects.filter(id__lte=term.id)
#        top3 = gen_top3(term_list, dealer)
#        set_answers("B10", data_sheet5, top3)

        #ycf new 由之前的年度top3平均分改为4个季度平均分
        term_list = Term.objects.filter(id__lte=term.id)        
        avg4 = gen_avg4(term_list, dealer)
        set_answers("B10", data_sheet5, avg4)
        
        dealer_region = dealer.parent.parent
        
        report_region_t1 = None
        report_region_t1 = Report.objects.filter(project=project, term=term1, dealer=dealer_region)
        if report_region_t1:
            report_region_t1 = report_region_t1[0]
        
        report_region_t2 = None
        report_region_t2 = Report.objects.filter(project=project, term=term2, dealer=dealer_region)
        if report_region_t2:
            report_region_t2 = report_region_t2[0]
        
        report_region_t3 = None
        report_region_t3 = Report.objects.filter(project=project, term=term3, dealer=dealer_region)
        if report_region_t3:
            report_region_t3 = report_region_t3[0]
            
        report_region = None
        report_region = Report.objects.filter(project=project, term=term, dealer=dealer_region)
        if report_region:
            report_region = report_region[0]
        
        
        score_dict_dealer_t1 = {}
        if report_t1:
            score_str_dealer_t1 = report_t1.score_str
            score_dict_dealer_t1 = str_to_pyobj(score_str_dealer_t1)
        
        score_dict_dealer_t2 = {}
        if report_t2:
            score_str_dealer_t2 = report_t2.score_str
            score_dict_dealer_t2 = str_to_pyobj(score_str_dealer_t2)
        
        score_dict_dealer_t3 = {}
        if report_t3:
            score_str_dealer_t3 = report_t3.score_str
            score_dict_dealer_t3 = str_to_pyobj(score_str_dealer_t3)
            
        score_dict_dealer = {}
        if report:
            score_str_dealer = report.score_str
            score_dict_dealer = str_to_pyobj(score_str_dealer)
        answer_dict_dealer = {}
        answer_str_dealer = report.answer_str
        if answer_str_dealer:
            answer_dict_dealer = str_to_pyobj(answer_str_dealer)
            #进店时间、离店时间
            time_in = answer_dict_dealer.get('time_in', '')
            time_out = answer_dict_dealer.get('time_out', '')
            set_answers("B7", data_sheet5, time_in)
            set_answers("B8", data_sheet5, time_out)
            if time_in and time_out:
                set_answers("B9", data_sheet5, time_out - time_in)
            
            #区域、全国排名
            region_rank = answer_dict_dealer.get('region_rank', '')
            nation_rank = answer_dict_dealer.get('nation_rank', '')
            set_answers("D10", data_sheet5, region_rank)
            set_answers("F10", data_sheet5, nation_rank)
        
        score_dict_region_t1 = {}
        if report_region_t1:
            score_str_region_t1 = report_region_t1.score_str
            score_dict_region_t1 = str_to_pyobj(score_str_region_t1)
        
        score_dict_region_t2 = {}
        if report_region_t2:
            score_str_region_t2 = report_region_t2.score_str
            score_dict_region_t2 = str_to_pyobj(score_str_region_t2)
        
        score_dict_region_t3 = {}
        if report_region_t3:
            score_str_region_t3 = report_region_t3.score_str
            score_dict_region_t3 = str_to_pyobj(score_str_region_t3)
            
        score_dict_region = {}
        if report_region:
            score_str_region = report_region.score_str
            score_dict_region = str_to_pyobj(score_str_region)
        
        score_dict_nation_t1 = {}
        if report_nation_t1:
            score_str_nation_t1 = report_nation_t1.score_str
            score_dict_nation_t1 = str_to_pyobj(score_str_nation_t1)
        
        score_dict_nation_t2 = {}
        if report_nation_t2:
            score_str_nation_t2 = report_nation_t2.score_str
            score_dict_nation_t2 = str_to_pyobj(score_str_nation_t2)
        
        score_dict_nation_t3 = {}
        if report_nation_t3:
            score_str_nation_t3 = report_nation_t3.score_str
            score_dict_nation_t3 = str_to_pyobj(score_str_nation_t3)
            
        score_dict_nation = {}
        if report_nation:
            score_str_nation = report_nation.score_str
            score_dict_nation = str_to_pyobj(score_str_nation)
            
        score_dict_max_nation = {}
        if report_max_nation:
            score_str_max_nation = report_max_nation.score_str
            score_dict_max_nation = str_to_pyobj(score_str_max_nation)
        
        score_dict_max_region = {}
        if report_max_region:
            score_str_max_region = report_max_region.score_str
            score_dict_max_region = str_to_pyobj(score_str_max_region)
        
#        #最终得分
        set_answers("B14", data_sheet5, score_dict_dealer_t1.get('score'))
        set_answers("B15", data_sheet5, score_dict_region_t1.get('score'))
        set_answers("B16", data_sheet5, score_dict_nation_t1.get('score'))
        
        set_answers("C14", data_sheet5, score_dict_dealer_t2.get('score'))
        set_answers("C15", data_sheet5, score_dict_region_t2.get('score'))
        set_answers("C16", data_sheet5, score_dict_nation_t2.get('score'))

        set_answers("D14", data_sheet5, score_dict_dealer_t3.get('score'))
        set_answers("D15", data_sheet5, score_dict_region_t3.get('score'))
        set_answers("D16", data_sheet5, score_dict_nation_t3.get('score'))
        
        set_answers("E14", data_sheet5, score_dict_dealer.get('score'))
        set_answers("E15", data_sheet5, score_dict_region.get('score'))
        set_answers("E16", data_sheet5, score_dict_nation.get('score'))
        
        #经销商得分与区域领先得分、全国领先得分对比
        set_answers("B19", data_sheet5, report.score)
        set_answers("C19", data_sheet5, score_dict_region.get('score'))
        set_answers("D19", data_sheet5, score_dict_max_region.get('score'))
        set_answers("E19", data_sheet5, score_dict_nation.get('score'))
        set_answers("F19", data_sheet5, score_dict_max_nation.get('score'))
        
        
        #经销商环节得分与区域得分、全国得分对比
        set_answers("B22", data_sheet5, score_dict_dealer.get('score'))
        set_answers("C22", data_sheet5, score_dict_dealer.get('A'))
        set_answers("D22", data_sheet5, score_dict_dealer.get('B'))
        set_answers("E22", data_sheet5, score_dict_dealer.get('C'))
        set_answers("F22", data_sheet5, score_dict_dealer.get('D'))
        set_answers("G22", data_sheet5, score_dict_dealer.get('E'))
        set_answers("H22", data_sheet5, score_dict_dealer.get('G'))
        
        set_answers("B23", data_sheet5, score_dict_region.get('score'))
        set_answers("C23", data_sheet5, score_dict_region.get('A'))
        set_answers("D23", data_sheet5, score_dict_region.get('B'))
        set_answers("E23", data_sheet5, score_dict_region.get('C'))
        set_answers("F23", data_sheet5, score_dict_region.get('D'))
        set_answers("G23", data_sheet5, score_dict_region.get('E'))
        set_answers("H23", data_sheet5, score_dict_region.get('G'))
        
        set_answers("B24", data_sheet5, score_dict_nation.get('score'))
        set_answers("C24", data_sheet5, score_dict_nation.get('A'))
        set_answers("D24", data_sheet5, score_dict_nation.get('B'))
        set_answers("E24", data_sheet5, score_dict_nation.get('C'))
        set_answers("F24", data_sheet5, score_dict_nation.get('D'))
        set_answers("G24", data_sheet5, score_dict_nation.get('E'))
        set_answers("H24", data_sheet5, score_dict_nation.get('G'))
        
        #环节得分概览
        set_answers("B31", data_sheet5, score_dict_dealer_t1.get('A'))
        set_answers("B37", data_sheet5, score_dict_dealer_t1.get('B'))
        set_answers("B43", data_sheet5, score_dict_dealer_t1.get('C'))
        set_answers("B49", data_sheet5, score_dict_dealer_t1.get('D'))
        set_answers("B55", data_sheet5, score_dict_dealer_t1.get('E'))
        set_answers("B61", data_sheet5, score_dict_dealer_t1.get('G'))
        
        set_answers("C31", data_sheet5, score_dict_dealer_t2.get('A'))
        set_answers("C37", data_sheet5, score_dict_dealer_t2.get('B'))
        set_answers("C43", data_sheet5, score_dict_dealer_t2.get('C'))
        set_answers("C49", data_sheet5, score_dict_dealer_t2.get('D'))
        set_answers("C55", data_sheet5, score_dict_dealer_t2.get('E'))
        set_answers("C61", data_sheet5, score_dict_dealer_t2.get('G'))
        
        set_answers("D31", data_sheet5, score_dict_dealer_t3.get('A'))
        set_answers("D37", data_sheet5, score_dict_dealer_t3.get('B'))
        set_answers("D43", data_sheet5, score_dict_dealer_t3.get('C'))
        set_answers("D49", data_sheet5, score_dict_dealer_t3.get('D'))
        set_answers("D55", data_sheet5, score_dict_dealer_t3.get('E'))
        set_answers("D61", data_sheet5, score_dict_dealer_t3.get('G'))
        
        set_answers("E31", data_sheet5, score_dict_dealer.get('A'))
        set_answers("E37", data_sheet5, score_dict_dealer.get('B'))
        set_answers("E43", data_sheet5, score_dict_dealer.get('C'))
        set_answers("E49", data_sheet5, score_dict_dealer.get('D'))
        set_answers("E55", data_sheet5, score_dict_dealer.get('E'))
        set_answers("E61", data_sheet5, score_dict_dealer.get('G'))
        
        data_sheet3 = ss.Sheets(3)
        write_sheet_3(data_sheet3, score_dict_dealer, score_dict_region, score_dict_nation, answer_dict_dealer)
        data_sheet4 = ss.Sheets(4)
        write_sheet_4(data_sheet4, score_dict_dealer, score_dict_region, score_dict_nation, answer_dict_dealer)
                
    except Exception, e:
        print 'error!', dealer.name, e
    finally:
        close_file(ss, x1)

if __name__ == "__main__":
    term1 = Term.objects.get(id=1)
    term2 = Term.objects.get(id=2)
    term3 = Term.objects.get(id=3)
    term = Term.objects.get(id=4)
    
    print 'generate bmw report...'
    project_bmw = Project.objects.get(id=1)
    gen_dealer_report(project_bmw, term, term1, term2, term3)
    print 'finish'
    
    print 'generate mini report...'
    project_mini = Project.objects.get(id=2)
    gen_dealer_report(project_mini, term, term1, term2, term3)
    print 'finish'
