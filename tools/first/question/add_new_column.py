#encoding:utf-8
import os, sys
sys.path.insert(0, os.path.abspath(os.curdir))

from django.conf import settings
from django.db.transaction import commit_on_success, set_dirty
from django.db import connection
from survey.models import Alternative, Question, Project, CheckPoint
import DbUtils

question_list = []
checkpoint_list = []

#@commit_on_success
#def add_new_respondentdata_column():
#    import DbUtils
#    c, db = DbUtils.cursor()
#    project1 = Project.objects.get(id=1)
#    project2 = Project.objects.get(id=2)
#    
#    q_list = Question.objects.filter(project=project2)
#    for q in q_list:
#        q_temp_list = Question.objects.filter(cid=q.cid,project=project1)
#        if len(q_temp_list) == 0:
#            question_list.append(q.cid)
#    
#    print question_list
#    for cid in question_list:
#        sql = 'alter table survey_respondentdata add column \'%s\' integer;' % cid
#        c.execute(sql)
#        sql = 'alter table survey_respondentdata add column \'%s__open\' varchar(1000);' % cid
#        c.execute(sql)
#    
#    set_dirty()
#
#@commit_on_success
#def add_new_reportdata_column():
#    import DbUtils
#    c, db = DbUtils.cursor()
#    project1 = Project.objects.get(id=1)
#    project2 = Project.objects.get(id=2)
#    
#    cp_list = CheckPoint.objects.filter(project=project2)
#    for cp in cp_list:
#        cp_temp_list = CheckPoint.objects.filter(name=cp.name,project=project1)
#        if len(cp_temp_list) == 0:
#            checkpoint_list.append(cp.name)
#    
#    print checkpoint_list
#    for cid in checkpoint_list:
#        sql = 'alter table mc_reportdata add column \'%s\' float;' % cid
#        c.execute(sql)
#    
#    set_dirty()

@commit_on_success
def add_respondentdata_column(project_id):
    project = Project.objects.get(id=project_id)
    sql = 'select * from survey_respondentdata where id = 1'
    try:
        c, con = DbUtils.cursor()
        c.execute(sql)
        column_names = [d[0] for d in c.description]
        q_list = Question.objects.filter(project=project)
        
        for q in q_list:
            if q.cid not in column_names:
                #屏蔽F49题的添加--原数据库中存在
                if 'F49' not in q.cid:
                    question_list.append(q.cid)
        
        print question_list
        for cid in question_list:
            if 'other' in cid or 'T3' or 'visitor_numb' == cid:
                sql = 'alter table survey_respondentdata add column \'%s\' varchar(1000);' % cid
                c.execute(sql)
                if con:
                    con.commit()
            else:
                sql = 'alter table survey_respondentdata add column \'%s\' integer;' % cid
                c.execute(sql)
                if con:
                    con.commit()
                sql = 'alter table survey_respondentdata add column \'%s__open\' varchar(1000);' % cid
                c.execute(sql)
                if con:
                    con.commit()
    finally:
        if c:
            c.close()
        if con:
            con.close() 

@commit_on_success      
def add_reportdata_column(project_id):
    project = Project.objects.get(id=project_id)
    sql = 'select * from mc_reportdata where id = 1'
    try:
        c, con = DbUtils.cursor()
        c.execute(sql)
        column_names = [d[0] for d in c.description]
        cp_list = CheckPoint.objects.filter(project=project)
        
        for cp in cp_list:
            if cp.name not in column_names:
                checkpoint_list.append(cp.name)
                
        print checkpoint_list
        for cid in checkpoint_list:
            sql = 'alter table mc_reportdata add column \'%s\' float;' % cid
            c.execute(sql)
            if con:
                con.commit()
    finally:
        if c:
            c.close()
        if con:
            con.close() 
    
def add_new_column(project_id):
    add_respondentdata_column(project_id)
    add_reportdata_column(project_id)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'need projectid!'
        sys.exit(1)
    project_id = sys.argv[1]
    add_new_column(project_id)
    