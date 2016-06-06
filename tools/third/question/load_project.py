#encoding:utf-8

import os, sys
sys.path.insert(0, os.path.abspath(os.curdir))

#from smk.question.models import *
from survey.models import *
from tools.first.question.load_checkpoint import update_checkpoint
from lxml import etree
from django.db.transaction import commit_on_success, commit, set_dirty
from survey import enums
from django.conf import settings
import json
import glob
import re
from mc.models import Term

term_list = [
    (u'2012年1月', 'W1', (2012, 1, 1, 0, 0, 0), (2012, 2, 1, 0, 0, 0)),
    (u'2012年2月', 'W2', (2012, 2, 1, 0, 0, 0), (2012, 3, 1, 0, 0, 0)),
    #(u'2012年3月','W3',(2012,3,1,0,0,0),(2012,4,1,0,0,0)),
]
    
def xml2tree(xmlfile):
    parser = etree.XMLParser(encoding='utf-8')
    tree = etree.parse(file(xmlfile), parser)
    return tree

@commit_on_success
def add_project(mm_file, term):
    basename = os.path.basename(mm_file)
    nametext = os.path.splitext(basename)[0].decode('gb18030')
    names = nametext.split('_')[1:]
    name = '_'.join(names)
    
    print u'\n初始化问卷：%s ...' % name
    project, create = Project.objects.get_or_create(name=name)
    
    print u'添加问题...'
    add_question(project, mm_file)
    return project
    
def add_question(project, mm_file):
    tree = xml2tree(mm_file)
    question_node_list = tree.xpath('/map/node/node')
    for question_node in question_node_list:
        node_text = question_node.attrib.get('TEXT')
        
        parts = node_text.split(':')
        if len(parts) < 3:
            print project.name
            print u'格式错误:', node_text, parts
            print u'题目的定义必须是:cid:question_title这种形式'
            sys.exit(1)
        question, create = Question.objects.get_or_create(cid=parts[1], project=project)
        question.name_abbr = parts[0]
        title = parts[2]
        question.title = title
        print title
        if len(parts) == 3:
            qtype = u'单选'
        else:
            qtype = parts[3].strip()
        
        if qtype == u'单选':
            question.questiontype = enums.QUESTION_TYPE_SINGLE            
        elif qtype == u'多选':
            question.questiontype = enums.QUESTION_TYPE_MULTIPLE
        elif qtype == u'填空':
            question.questiontype = enums.QUESTION_TYPE_BLANK
        elif qtype == u'多项填空':
            question.questiontype = enums.QUESTION_TYPE_MULTIPLE_BLANK
        elif qtype == u'多项打分':
            question.questiontype = enums.QUESTION_TYPE_MULTIPLE_SCORE
        else:
            print u'qtype not supported yet. [ %s ]' % qtype
            sys.exit()
        
        question.save()
        
        if qtype in [u'单选', u'多选', u'多项填空', u'多项打分']:
            alt_node_list = question_node.getchildren()
            if not alt_node_list:
                #Alternative(cid='A1',title=u'是',question=question,score=100).save()
                #Alternative(cid='A2',title=u'否',question=question,open=True,score=0).save()
                #Alternative(cid='A3',title=u'不适用',question=question,open=True,score=None).save()
                a1, create = Alternative.objects.get_or_create(cid='A1', title=u'是', question=question, score=100)
                a1.save()
                a2, create = Alternative.objects.get_or_create(cid='A2', title=u'否', question=question, open=True, score=0)
                a2.save()
                a3, create = Alternative.objects.get_or_create(cid='A3', title=u'不适用', question=question, open=True, score=None)
                a3.save()
            else:
                a_index = 0
                
                for alt_node in alt_node_list:
                    a_index += 1
                    if qtype == u'单选' and a_index == 1:
                        score = 100
                    elif qtype == u'单选' and a_index == 2:
                        score = 0
                    else:
                        score = None
                    alt, create = Alternative.objects.get_or_create(cid='A%s' % a_index, title=alt_node.attrib.get('TEXT'), question=question, score=score)
                    if alt_node.getchildren() and alt_node.getchildren()[0].attrib.get('TEXT').find(u'开放') > -1:
                        alt.open = True
                        alt_alt_node_list = alt_node.getchildren()
                        if alt_alt_node_list:
                            for alt_alt_node in alt_alt_node_list:
                                alt_text = alt_alt_node.attrib.get('TEXT')
                                alt_text_list = alt_text.split(':')
                                if len(alt_text_list) == 2:
                                    multiple_text = alt_text_list[1]
                                    a_list = alt_alt_node.getchildren()
                                    if a_list:
                                        for a in a_list:
                                            a_texts = a.attrib.get('TEXT').split(':')
                                            a_cid = a_texts[0]
                                            a_title = a_texts[1]
                                            alt_alt, create = Alternative.objects.get_or_create(cid=a_cid, title=a_title, question=question, score=None)
                                            if multiple_text == u'多选':
                                                alt_alt.multiple = True
                                            if a_cid == '98':
                                                alt_alt.open = True
                                            alt_alt.save()
                                            print a_cid, a_title
                    alt.save()


@commit_on_success
def add_all_project():
    mm_list = []
    for mm_file in glob.glob(os.path.join(settings.RESOURCES_ROOT, 'first/mm', 'project_*.mm')):
        mm_list.append(mm_file)
    
    terms = Term.objects.all().order_by('-id')
    term = terms[0]
    
    mm_list.sort()
    for m in mm_list:
        project = add_project(m, term)
        set_dirty()
        update_checkpoint(project.id)
    set_dirty()
    
@commit_on_success
def add_question_qa_cn(project):
    import xlrd
    xlsfile = os.path.join(settings.RESOURCES_ROOT, u"third/QA/2012_Aftersales Mystery Shopping_updated Q'naire Q&A_CN_20120802.xls")
    book = xlrd.open_workbook(xlsfile)
    
    sh = book.sheet_by_index(0)
    #print sh.name, sh.nrows, sh.ncols
    for rx in range(11, sh.nrows):
        texts = sh.row_values(rx)
#        print texts
        #texts = sh.row(rx)
        if len(texts) >= 6:
            cids = texts[1].strip()
            q_desc = texts[3].strip()
            q_addon = texts[4].strip()
            a_desc = texts[5].strip()
            
            try:
                question = Question.objects.get(name_abbr=cids, project=project)
            except Question.DoesNotExist:
                print 'no question', cids
                continue
            
            qa, create = QuestionQA.objects.get_or_create(question=question)
            qa.q_desc = q_desc
            qa.q_addon = q_addon
            qa.a_desc = a_desc
            
            qa.save()
    
def add_question_qa_en(project):
    #QuestionQA.objects.all().delete()
    import xlrd
    xlsfile = os.path.join(settings.RESOURCES_ROOT, u"third/QA/2012_Aftersales Mystery Shopping_updated Q'naire Q&A_EN_20120802.xls")
    book = xlrd.open_workbook(xlsfile)
    _read_qa_from_xls(project, book, chinese=False)

#@commit_on_success
#def add_question_qa():
#    add_question_qa_cn()
#    add_question_qa_en()
    
def _read_qa_from_xls(project, book, chinese=True):
    sh = book.sheet_by_index(0)
    #print sh.name, sh.nrows, sh.ncols
    for rx in range(10, sh.nrows):
        texts = sh.row_values(rx)
        #texts = sh.row(rx)
        if len(texts) >= 6:
            cids = texts[1].strip()
            q_desc = texts[3].strip()
            q_addon = texts[4].strip()
            a_desc = texts[5].strip()
            
            cids = cids.replace(u'.', '')
            cids = cids.replace(u'．', '')
            try:
                question = Question.objects.get(name_abbr=cids, project=project)
            except Question.DoesNotExist:
                print 'no question2', cids
                continue
            
            qa, create = QuestionQA.objects.get_or_create(question=question)
            if chinese:
                qa.q_desc = q_desc
                qa.q_addon = q_addon
                qa.a_desc = a_desc
            else:
                qa.q_desc_en = q_desc
                qa.q_addon_en = q_addon
                qa.a_desc_en = a_desc                
                qa.q_en = texts[2].strip()
            
            qa.save()
            
def loader():
    #add_all_project()
    project = Project.objects.get(id=2)
    add_question_qa_cn(project)
    add_question_qa_en(project)
    
if __name__ == '__main__':
    loader()
