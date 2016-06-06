#encoding:utf-8
from survey.models import Project
from mcview.decorator import cached
@cached('project_all_2012')
def get_2012_projects():
    #id=1的为2011年问卷模板
    return Project.objects.filter(id__gt=1)

@cached('project_id_map')
def get_project_id_map():
    projects = Project.objects.all()
    project_map = {}
    for p in projects:
        project_map[p.id] = p
    return project_map

def get_project_by_id(project_id):
    return get_project_id_map().get(project_id, None)

def get_project_by_id(project_id):
    return Project.objects.get(id=project_id)
