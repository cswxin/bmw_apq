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


def excel2report(term,dtype):
    project = Project.objects.get(id=1)
    dealertype = DealerType.objects.get(name_cn='BMW')
    
    dealer = Dealer.objects.get_or_create(name='37249')[0]
    report= Report.objects.get_or_create(project=project, dealer=dealer, term=term ,dealertype=dealertype)[0]
    score_str = report.score_str
#    answer_str = report.answer_str
    if score_str:
        answer_dict = str_to_pyobj(score_str)
        print answer_dict
        
        
if __name__ == '__main__':
    term = Term.objects.get(id=1)
    excel2report(term,'bmw')
