#encoding:utf-8
import os, sys
sys.path.insert(0, os.path.abspath(os.curdir))
from survey.models import Question, CheckPoint
from mc.models import Paper, Report
from survey.q_models import get_q_model
import DbUtils

class Field(object):
    def __init__(self, adict):
        self.name = adict.get('name')
        try:
            self.type = field_type_dict[adict.get('type')]
        except KeyError, ex:
            print self.name, type, self.length
            raise ex
        self.length = int(adict.get('length', 255))            
    
    def __str__(self):
        if self.type in ['integer', 'datetime', 'float']:
            return '%s %s' % (self.name, self.type)
        else:
            return '%s %s(%s)' % (self.name, self.type, self.length)

field_type_dict = {
    'int':'integer',
    'bool':'integer',
    'varchar':'varchar',
    'datetime':'datetime',
    'float':'float',
#    'char':'char',
}

def get_respondent_field_list(project_id):
    column_list = [
        dict(name='id', type='int'),
    ]
    question_list = Question.objects.filter(project=project_id).order_by('listorder', 'id')
    for question in question_list:
        q_model = get_q_model(question)        
        column_list.extend(q_model.get_column_list())
    field_list = [Field(column) for column in column_list]
    return field_list

def create_respodentdata_table(project_id):
    field_list = get_respondent_field_list(project_id)
    field_str = ','.join(str(field) for field in field_list)
    sql = 'create table if not exists survey_respondentdata (%s);' % (field_str)
#    print sql
    try:
        c, con = DbUtils.cursor()
        c.execute(sql)
        if con:
            con.commit()
    finally:
        if c:
            c.close()
        if con:
            con.close() 

def get_report_field_list(project_id):
    column_list = [
        dict(name='id', type='int'),
        dict(name='total', type='float'),
    ]
    
    cp_group_list = CheckPoint.objects.filter(has_child=True,project__id=project_id).order_by('id')
    for cp_group in cp_group_list:
        column_list.append(dict(name=cp_group.name, type='float'))
        for sub_cp in CheckPoint.objects.filter(parent=cp_group).order_by('id'):
            if sub_cp.name in ['Q7c','Q34c','Q44c','Q62','Q63','Q64']:
                column_list.append(dict(name=sub_cp.name, type='varchar'))
            else:
                column_list.append(dict(name=sub_cp.name, type='float'))
    field_list = [Field(column) for column in column_list]
    return field_list

def create_reportdata_table():
    project_id = 1
    field_list = get_report_field_list(project_id)
    field_str = ','.join(str(field) for field in field_list)
    sql = 'create table if not exists mc_reportdata (%s);' % (field_str)
    print sql
    try:
        c, con = DbUtils.cursor()
        c.execute(sql)
        if con:
            con.commit()
    finally:
        if c:
            c.close()
        if con:
            con.close() 

def get_report_resp_column_mapping(project_id):
    column_mapping = {}
    cp_list = CheckPoint.objects.filter(has_child=False).order_by('id')
    for cp in cp_list:
        q_model = get_q_model(cp.question)        
        column_mapping[cp.name] = q_model.get_column_list()[0]['name']
    
    return column_mapping

QUESTION_LIST_DICT = {}
def get_question_list(project_id):
    project_id = int(project_id)
    question_list = QUESTION_LIST_DICT.get(project_id)
    if not question_list:
        question_list = list(Question.objects.filter(project=project_id).order_by('listorder', 'id'))
        QUESTION_LIST_DICT[project_id] = question_list
    return question_list

#根据paper的id获取问卷答案的字典
def get_respondentdata_dict_by_pid(paper_id):
    paper = Paper.objects.get(id=paper_id)
    return get_respondentdata_dict_by_paper(paper)

#根据paper的id获取问卷答案的字典
def get_respondentdata_dict_by_paper(paper):
    respondentdata_id = paper.respondent.id
    sql = 'select * from survey_respondentdata where id = %s' % respondentdata_id
    try:
        c, con = DbUtils.cursor()
        c.execute(sql)
        column_names = [d[0] for d in c.description]
        list = []
        row = c.fetchone()
        for index, r in enumerate(row):
            list.append((column_names[index], r))
    finally:
        if c:
            c.close()
        if con:
            con.close() 
    return dict(list)

#根据dealer的id和term的id获取问卷分数的字典
def get_reportdata_dict_by_pid(paper_id):
    paper = Paper.objects.get(id=paper_id)
    return get_reportdata_dict_by_paper(paper)
def get_reportdata_dict_by_report(report):
    if report:
        sql = 'select * from mc_reportdata where id = %s' % report.id
        try:
            c, con = DbUtils.cursor()
            c.execute(sql)
            column_names = [d[0] for d in c.description]
            list = []
            row = c.fetchone()
            for index, r in enumerate(row):
                list.append((column_names[index], r))
        finally:
            if c:
                c.close()
            if con:
                con.close() 
        return dict(list)
    else:
        return None
def get_reportdata_dict_by_paper(paper):
    reports = Report.objects.filter(respondent=paper.respondent)
    if reports:
        report = reports[0]
        return get_reportdata_dict_by_report(report)
    else:
        return None
if __name__ == '__main__':
#    create_respodentdata_table(1)
    create_reportdata_table()
    
