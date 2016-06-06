#encoding:utf-8
import os, sys
if __name__ == '__main__':
    sys.path.insert(0, os.path.abspath(os.curdir))

from survey.models import Project, AlternativeAttribute, Alternative, MatrixRow, Question, QuestionAttribute
from mc.models import Term
from lxml import etree
from django.db.transaction import commit_on_success, set_dirty
from survey import enums
from django.conf import settings
import glob
import re
import datetime

script_path = settings.SITE_ROOT

term_list = [
    (u'第一期', 2013, (2013, 1, 1, 0, 0, 0), (2013, 2, 1, 0, 0, 0)),
]

def add_term():
    terms = Term.objects.all()
    for term in terms:
        term.is_active = False
        term.is_active_input = False
        term.save()

    for name, year, begin, end in term_list:
        term, create = Term.objects.get_or_create(name=name)
        term.name = name
        term.year = year
        term.begin = datetime.datetime(*begin)
        term.end = datetime.datetime(*end)
        term.is_active = False
        term.save()

    #开放最后期数
    term.is_active = True
    term.is_active_input = True
    term.save()

def xml2tree(xmlfile):
    parser = etree.XMLParser(encoding='utf-8')
    tree = etree.parse(file(xmlfile), parser)
    return tree

@commit_on_success
def add_questionnaire(mm_file, term):
    basename = os.path.basename(mm_file)
    nametext = os.path.splitext(basename)[0].decode('gb18030')
    names = nametext.split('_')[1:]
    name = '_'.join(names)

    print u'\n初始化问卷：%s ...' % name

    project, is_create = Project.objects.get_or_create(name=name)
    project.save()
    #~ if is_create:
#    print u'设置项目属性...'
#    add_questionnaire_custom_attr(questionnaire)

    print u'添加问题...'
    add_question(project, mm_file)

#def add_questionnaire_custom_attr(questionnaire):
#    #去掉ip控制，cookie控制
#    attr, is_create = QuestionnaireAttribute.objects.get_or_create(questionnaire=questionnaire, attr_name='answer_per_ip')
#    attr.attr_value = -1
#    attr.save()
#    attr, is_create = QuestionnaireAttribute.objects.get_or_create(questionnaire=questionnaire, attr_name='no_cookie_restrict')
#    attr.attr_value = -1
#    attr.save()
#    attr, is_create = QuestionnaireAttribute.objects.get_or_create(questionnaire=questionnaire, attr_name='show_pre_button')
#    attr.attr_value = 1
#    attr.save()
#    attr, is_create = QuestionnaireAttribute.objects.get_or_create(questionnaire=questionnaire, attr_name='no_countdown')
#    attr.attr_value = 1
#    attr.save()

re1 = re.compile(r'[A-Z][a-z0-9]+')

def add_question(project, mm_file):
    tree = xml2tree(mm_file)
    question_node_list = tree.xpath('/map/node/node/node')
    listorder = 0
    for question_node in question_node_list:
        node_text = question_node.attrib.get('TEXT')
        #~ print node_text,project.id
        parts = node_text.split(':')
        print parts
        if len(parts) < 1:
            print project.name
            print u'格式错误:', node_text, parts
            print u'题目的定义必须是:cid:name_abbr:question_title这种形式'
            sys.exit(1)

        question, created = Question.objects.get_or_create(cid=parts[0], project=project)
#        question.name_abbr = parts[0]
        title = parts[1]
        question.title = title

        if len(parts) == 2:
            qtype = u'单选'
        else:
            qtype = parts[2].strip()

        if qtype == u'单选':
            question.questiontype = enums.QUESTION_TYPE_SINGLE
            question.max_answer_num = -1
        elif qtype == u'多选':
            question.questiontype = enums.QUESTION_TYPE_MULTIPLE
            question.max_answer_num = -1
        elif qtype == u'填空':
            question.questiontype = enums.QUESTION_TYPE_BLANK
        elif qtype == u'多项填空':
            question.questiontype = enums.QUESTION_TYPE_MULTIPLE_BLANK
        elif qtype == u'多项打分':
            question.questiontype = enums.QUESTION_TYPE_MULTIPLE_SCORE
            question.max_answer_num = 10
        elif qtype == u'打分':
            question.questiontype = enums.QUESTION_TYPE_SCORE
            question.max_answer_num = 10
        elif qtype == u'排序':
            question.questiontype = enums.QUESTION_TYPE_ORDER
            question.max_answer_num = -1
        elif qtype == u'描述':
            question.questiontype = enums.QUESTION_TYPE_DESC
        elif qtype == u'不定项':
            question.questiontype = enums.QUESTION_TYPE_VARIABLE
        elif qtype == u'矩阵单选':
            question.questiontype = enums.QUESTION_TYPE_MATRIX_SINGLE

        else:
            print u'qtype not supported yet. [ %s ]' % qtype
            print project.name
            print question.cid
            sys.exit(1)

        alt_node_list = question_node.getchildren()

        #判断整个题目是否不计分
        for alt in alt_node_list:
            #~ print alt.attrib.get('TEXT'),project.id,node_text
#            print alt.attrib.get('TEXT')
            alt_node = alt.attrib.get('TEXT').strip()
            if alt_node.find('w:none') != -1:
                question.is_count = False
            else:
                question.is_count = True

            if alt_node.startswith("count"):
                matrix_count = alt_node.split(":")[1]
                question.matrix_count = matrix_count
            if alt_node.startswith("w:"):
                weight = alt_node.split(":")[1]
                question.weight = weight

            if alt_node.startswith("show_type"):
                question.question_show_type = enums.QUESTION_SHOW_TYPE_SELECT

        listorder += 1
        question.listorder = listorder
        question.save()

        if qtype == u'矩阵单选':

            m_index = 0
            matrix_listorder = 0
            for matrix_node in alt_node_list:
                #创建子题干
                matrix_text = matrix_node.attrib.get('TEXT').strip()
                if matrix_text.startswith('w:') or matrix_text.startswith('count'):
                    continue

                matrix_listorder += 1
                m_index += 1
                matrix_cid = 'A%s' % m_index
                matrix, created = MatrixRow.objects.get_or_create(cid=matrix_cid, question=question)
                matrix.alttext = matrix_text
                matrix.listorder = matrix_listorder
                matrix.save()

                #创建选项
                alt_node_list = matrix_node.getchildren()
                a_index = 0
                for alt_node in alt_node_list:
                    #题目中w:none 不计分 则直接跳过
                    alt_node_text = alt_node.attrib.get('TEXT').strip()
                    if alt_node_text.startswith('w:') or alt_node_text.startswith('count'):
                        continue

                    a_index += 1
                    create_altnode(alt_node, qtype, a_index, matrix=matrix, question=question)

        if qtype in [u'单选', u'多选', u'多项填空', u'多项打分', u'打分', u'排序', u'不定项']:
            if not alt_node_list:
                pass

            else:
                a_index = 0
                for alt_node in alt_node_list:
                    #题目中w:none 不计分 则直接跳过
                    alt_node_text = alt_node.attrib.get('TEXT').strip()
                    if alt_node_text.startswith('w:none') or alt_node_text.startswith('show_type') :
                        continue

                    a_index += 1
                    create_altnode(alt_node, qtype, a_index, question=question)

                if not alt_node.attrib.get('TEXT'):
                    print 'error!'
                    print node_text
                    print alt_node

        if question.questiontype == enums.QUESTION_TYPE_SCORE:
            add_question_attribute(question, 'disp_type', 'score_colorbar')
            add_question_attribute(question, 'need_reason_for_score', '1,2,3,4,5,6,7,8,9,10')

        if question.questiontype == enums.QUESTION_TYPE_BLANK:
            node_list = question_node.getchildren()

            if  node_list:
                for node in  node_list:
                    if node.attrib.get('TEXT').strip() == "textarea" or node.attrib.get('TEXT').strip() == u"附加属性":
                        add_question_attribute(question, 'disp_type', 'textarea')
                    if node.attrib.get('TEXT').strip() == "visit_date":
                        #~ print question.id
                        add_question_attribute(question, 'validate_js', 'check_date')

                    if node.attrib.get('TEXT').strip() == "visit_begin_time" or node.attrib.get('TEXT').strip() == "visit_end_time":
                        #question.title += u'（格式:hhmm；4位数字，如1805表示18点05分）'
                        add_question_attribute(question, 'validate_js', 'check_time')

                    if node.attrib.get('TEXT').strip() == "phone":
                        add_question_attribute(question, 'validate_js', 'isTel')
                    if node.attrib.get('TEXT').strip() == "check_date":
                        add_question_attribute(question, 'validate_js', 'check_date')

                    if node.attrib.get('TEXT').strip() == "check_time":
                        add_question_attribute(question, 'validate_js', 'check_time')
                    if node.attrib.get('TEXT').strip() == "check_mobile":
                        add_question_attribute(question, 'validate_js', 'check_mobile')
                    if node.attrib.get('TEXT').strip() == "check_number":
                        add_question_attribute(question, 'validate_js', 'check_number')
                    if node.attrib.get('TEXT').strip() == "check_number_or_letter":
                        add_question_attribute(question, 'validate_js', 'check_number_or_letter')

            # 维护老的录入方式
            if 'visit_date' in question.cid:
                #question.title += u'（格式:mmdd；4位数字，如1104表示11月4日）'
                add_question_attribute(question, 'validate_js', 'check_date')

            if 'visit_begin_time' in question.cid or 'visit_end_time' in question.cid:
                #question.title += u'（格式:hhmm；4位数字，如1805表示18点05分）'
                add_question_attribute(question, 'validate_js', 'check_time')

            if "phone" in question.cid:
                #(8到15位数)
                add_question_attribute(question, 'validate_js', 'isTel')


def create_altnode(alt_node, qtype, a_index, matrix=None, question=None):
    weight = '0'
    go = ''
    #判断是否计分，mm文件中w:none 则为不计分
    is_count = True
    need_comments = False

    check_number = False
    if qtype == u'单选' or  qtype == u'多选' or qtype == u'不定项' or qtype == u'矩阵单选' and not alt_node.attrib.get('TEXT').startswith("w"):
        node_tmps = alt_node.getchildren()

        for node_tmp in node_tmps:
            node_str = node_tmp.attrib.get('TEXT').strip()
            if node_str.startswith("w"):
                weight = node_str.split(":")[1]

                if weight.strip() == "none":
                    is_count = False
                else:
                    is_count = True

            if node_str.startswith("go"):
                go = node_str.split(":")[1]

            if node_str == u'开放':
                need_comments = True
            if node_str == u'不定项':
                listorder = 0

            if node_str.startswith("check_number"):
                check_number = True



    alt_parts = alt_node.attrib.get('TEXT').strip()
#    if 'S3' in question.cid and u'家人/亲戚/朋友' in question.title:
#        if u'其它' == alt_parts:
#            a_index = 97
    alt_cid = 'A%s' % a_index
    alttext = alt_parts
    if matrix:
        alt, created = Alternative.objects.get_or_create(cid=alt_cid, matrix=matrix, question=question)
    else:
        alt, created = Alternative.objects.get_or_create(cid=alt_cid, question=question)

    alt.alttext = alttext
    alt.need_comments = need_comments
    alt.go = go
    alt.listorder = a_index

    #选择是的情况下,保存分数 否为0分  不涉及 则is_count 为False
    if weight and weight.strip() != "none":
        weight_list = weight.split('_')
        alt.weight = weight_list[0]
        if len(weight_list) == 3:
            alt.weight2 = weight_list[1]
            alt.weight3 = weight_list[2]

    if is_count:
        if alttext == u'不涉及':
            is_count = False
    #不计分
    alt.is_count = is_count
    alt.save()

    if check_number:
        add_alternative_attribute(alt, 'validate_js', 'check_number')

def add_alternative_attribute(alternative, attr_name, attr_value):
    attr, is_create = AlternativeAttribute.objects.get_or_create(alternative=alternative, attr_name=attr_name)
    attr.attr_value = attr_value
    attr.save()

def add_question_attribute(question, attr_name, attr_value):
    attr, is_create = QuestionAttribute.objects.get_or_create(question=question, attr_name=attr_name)
    attr.attr_value = attr_value
    attr.save()

@commit_on_success
def add_all_questionnaire():
    mm_list = []
    for mm_file in glob.glob(os.path.join(script_path, 'mm', 'project_2015*.mm')):
        mm_list.append(mm_file)

    terms = Term.objects.all().order_by('-id')
    term = terms[0]

    mm_list.sort()
    for m in mm_list:
        add_questionnaire(m, term)

    set_dirty()

if __name__ == '__main__':
    add_all_questionnaire()
