#encoding:utf-8
import os, sys
sys.path.insert(0, os.path.abspath(os.curdir))
from survey.models import CheckPoint, Project
import DbUtils
from django.db.transaction import commit_on_success, set_dirty

class Field(object):
    def __init__(self, adict):
        self.name = adict.get('name')
        try:
            self.type = field_type_dict[adict.get('type')]
        except KeyError, ex:
            print self.name, type, self.length
            raise ex
        self.length = int(adict.get('length', 1))            
    
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
}

def get_other_report_field_list(project_id):
    column_list = [
        dict(name='id', type='int'),
        dict(name='total', type='float'),
    ]
    
    cp_group_list = CheckPoint.objects.filter(has_child=True, project__id=project_id).order_by('id')
    for cp_group in cp_group_list:
        column_list.append(dict(name=cp_group.name, type='float'))
        for sub_cp in CheckPoint.objects.filter(parent=cp_group, project__id=project_id).order_by('id'):
            column_list.append(dict(name=sub_cp.name, type='float'))
    field_list = [Field(column) for column in column_list]
    return field_list

@commit_on_success
def create_otherreportdata_table(project_id):
    field_list = get_other_report_field_list(project_id)
    field_str = ','.join(str(field) for field in field_list)
    sql = 'create table if not exists mc_otherreportdata (%s);' % (field_str)
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

@commit_on_success
def add_reportdata_column(project_id):
    checkpoint_list = []
    project = Project.objects.get(id=project_id)
    sql = 'select * from mc_otherreportdata where id = 1'
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
            sql = 'alter table mc_otherreportdata add column \'%s\' float;' % cid
            c.execute(sql)
            if con:
                con.commit()
    finally:
        if c:
            c.close()
        if con:
            con.close() 

if __name__ == '__main__':
    create_otherreportdata_table(1)
    add_reportdata_column(2)
    add_reportdata_column(3)
    add_reportdata_column(4)
    
