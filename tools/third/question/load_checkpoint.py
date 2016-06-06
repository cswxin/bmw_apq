#encoding:utf-8

import os,sys,glob,re
sys.path.insert(0,os.path.abspath(os.curdir))

from survey.models import *

from lxml import etree
from django.db.transaction import commit_on_success,commit_manually,commit,set_dirty
import string
from django.conf import settings

def xml2tree(xmlfile):
    parser = etree.XMLParser(encoding='utf-8')
    tree = etree.parse(file(xmlfile), parser)
    return tree

QUESTION_CID_DICT = None

def _get_question_dict():
    global QUESTION_CID_DICT
    if not QUESTION_CID_DICT:
        QUESTION_CID_DICT = dict([((q.cid,q.project_id),q) for q in Question.objects.all()])
    return QUESTION_CID_DICT

def add_checkpoint(project_id, node, node_name,parent=None): 
    question_cid_dict = _get_question_dict()
    
    nodetext = node.attrib.get('TEXT')
    
    nodetext = nodetext.strip()
    child_list = node.getchildren()
    splits = nodetext.split(':')
    
    question = question_cid_dict.get((splits[0],project_id))
    if question:
        cp,created = CheckPoint.objects.get_or_create(question = question, project__id = project_id)
        cp.name_abbr = question.name_abbr
        cp.desc = question.title
    else:
        cp,created = CheckPoint.objects.get_or_create(name = node_name, project__id = project_id)
        cp.name_abbr = node_name
        cp.desc = nodetext
    
    cp.project_id = project_id
    cp.parent = parent
    
    if child_list:
        cp.name = node_name
        cp.has_child = True
        cp.save()
    else:
        
        #检查点下无问题
        if 'none' in node.attrib.get('TEXT'):
            cp.name = node_name
            cp.has_child = True
            cp.save()
            return
            
        if ':' in node.attrib.get('TEXT'):
            cp.desc,cp.resp_col = node.attrib.get('TEXT').split(':')[:2]
            cp.name = cp.desc
        else:
            cp.resp_col = cp.name = node.attrib.get('TEXT').strip()
        question = question_cid_dict.get((cp.name,project_id))
        cp.question = question
        cp.desc = question.title
        cp.has_child = False
        cp.save()
        print cp.resp_col,cp.desc
    
    for child in child_list:
        child_name = child.attrib.get('TEXT')
        add_checkpoint(project_id, child, child_name, cp)

@commit_on_success
def update_checkpoint(project_id):
    p = Project.objects.get(id=project_id)
    group_index = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','W']
    print 'Add checkpoint for project %s' % p.name
    try:
        design_file = os.path.join(settings.RESOURCES_ROOT,'first/mm',u'checkpoint_%s.mm' % p.name)
        tree = xml2tree(design_file)
    except IOError:
        print 'IOError',design_file
        
    group_node_list = tree.xpath(u'/map/node/node')
    
    index = 0
    for node in group_node_list:
        add_checkpoint(p.id,node, group_index[index])
        index += 1
        
    set_dirty()
    
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'need projectid!'
        sys.exit(1)
    project_id = sys.argv[1]
    update_checkpoint(project_id)
