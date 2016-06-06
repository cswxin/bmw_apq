#encoding:utf-8
import os, sys
if __name__ == '__main__':
    sys.path.insert(0, os.path.abspath(os.curdir))

import os, time, datetime
from django.db.transaction import commit_on_success, commit, set_dirty
from django.conf import settings
from mc.models import Term

term_list = [
    (u'2012年第一期', 'W1', (2012, 1, 1, 0, 0, 0), (2012, 4, 1, 0, 0, 0)),
    #(u'2012年2月','W2',(2012,2,1,0,0,0),(2012,3,1,0,0,0)),
    #(u'2012年3月','W3',(2012,3,1,0,0,0),(2012,4,1,0,0,0)),
]

@commit_on_success
def add_new_term():
    terms = Term.objects.all()
    for term in terms:
        term.is_active = False
        term.is_active_input = False
        term.save()
    
    for name, name_en, begin, end in term_list:
        term, create = Term.objects.get_or_create(name=name)
        term.name = name
        term.name_en = name_en
        term.name_cn = name
        term.begin = datetime.datetime(*begin)
        term.end = datetime.datetime(*end)
        term.is_active = False
        term.save()
    
    #开放最后期数
    term.is_active = True
    term.is_active_input = True
    term.save()
    
if __name__ == '__main__':
    add_new_term()
