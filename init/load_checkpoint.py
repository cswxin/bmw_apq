#encoding:utf-8

import os, sys
sys.path.insert(0, os.path.abspath(os.curdir))

from survey.models import Question, CheckPoint, Project
from mc.models import Term
from lxml import etree
from django.db.transaction import commit_on_success, set_dirty
from django.conf import settings
script_path = settings.SITE_ROOT

def xml2tree(xmlfile):
    parser = etree.XMLParser(encoding='utf-8')
    tree = etree.parse(file(xmlfile), parser)
    return tree

QUESTION_CID_DICT = None

def _get_question_dict():
    global QUESTION_CID_DICT
    if not QUESTION_CID_DICT:
        QUESTION_CID_DICT = dict([((q.cid, q.project.id), q) for q in Question.objects.all()])
    return QUESTION_CID_DICT

def add_checkpoint(project, node, node_name, parent=None):
    question_cid_dict = _get_question_dict()

    nodetext = node.attrib.get('TEXT')
    print nodetext
    nodetext = nodetext.strip()
    if nodetext.startswith('w:'):
        return
    show_type = 1
    if ':' in nodetext:
        show_type = int(nodetext.split(':')[1])
        nodetext = nodetext.split(':')[0]
    if parent:
        show_type = parent.show_type

    child_list = node.getchildren()

    question = question_cid_dict.get((nodetext, project.id))
    if question:
        cp, created = CheckPoint.objects.get_or_create(question=question)
#        cp.name_abbr = question.name_abbr
        cp.desc = question.title
    else:
        cp, created = CheckPoint.objects.get_or_create(project=project, name=node_name)
#        cp.name_abbr = node_name
        cp.desc = nodetext

    cp.project = project
    cp.parent = parent
    cp.show_type = show_type

    if child_list:
        score = _get_weight(node)
        cp.score = score

        cp.name = node_name
        cp.has_child = True
        cp.save()

    #保存除环节和w开头的计分项之外的 所有题目
    else:
        cp.resp_col = cp.name = node.attrib.get('TEXT').strip()
        cp.has_child = False
        cp.save()

    i = 0
    for child in child_list:
        i += 1
        child_name = '%s%s' % (node_name, i)
        add_checkpoint(project, child, child_name, cp)

#获得权重
def _get_weight(node):
    child_list = node.getchildren()
    if not child_list:
        return

    score = 0.0
    for c in child_list:
        nodetext = c.attrib.get('TEXT')
        #~ print nodetext
        ws = nodetext.split(':')
        if len(ws) == 2:
            score = float(ws[1].strip())

    return score

@commit_on_success
def update_checkpoint():
    terms = Term.objects.all().order_by('-id')

    project_list = Project.objects.all()
    for project in project_list:
        if project.id == 1 or project.id == 2:
            continue
        group_index = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']
        print 'Add checkpoint for project %s' % project.name
        try:
            design_file = os.path.join(script_path, 'mm', u'checkpoint_%s.mm' % project.name)
            tree = xml2tree(design_file)
        except IOError:
            print 'IOError', design_file

        group_node_list = tree.xpath(u'/map/node/node')

        index = 0
        for node in group_node_list:
            #~ print group_index[index]
            add_checkpoint(project, node, group_index[index])
            index += 1

    set_dirty()

if __name__ == '__main__':
    update_checkpoint()
