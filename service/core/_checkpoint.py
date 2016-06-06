#encoding:utf-8
from survey.models import CheckPoint
import constant
from mcview.decorator import cached


def get_define_cp_total_list():
    total = CheckPoint()
    total.name = 'total'
#    total.name_abbr = 'Total'
    total.desc = u'总得分'
    total.desc_en = 'Total Score'
    max = CheckPoint()
    max.name = 'max_total'
#    max.name_abbr = 'Max'
    max.desc = u'最高分'
    max.desc_en = 'Max Total Score'
    min = CheckPoint()
    min.name = 'min_total'
#    min.name_abbr = 'Min'
    min.desc = u'最低分'
    min.desc_en = 'Min Total Score'
    
    checkpoint_group_list = [total, max, min]
    return checkpoint_group_list

def get_project_cp_group_list(project_id):
    @cached('cp_group_list_pro%s' % str(project_id))
    def __inner():
        cp_group_list = CheckPoint.objects.filter(parent=None, project__id=project_id).exclude(name='F').order_by('id')
#        for cp in cp_group_list:
#            cp.sub_count = CheckPoint.objects.filter(parent=cp).count()
        return cp_group_list
    return __inner()

def get_checkpoint_group_list_with_total(project_id):
    @cached('cp_group_list_with_total_%d' % project_id)
    def inner():
        total = CheckPoint()
        total.name = 'Total'
        total.name_abbr = 'Total'
        total.desc = u'总得分'
        total.desc_en = 'Total Score'
        total.has_child = True
        cp_group_list = [total]
        cp_group_list.extend(get_project_cp_group_list(project_id))
        for i, cp in enumerate(cp_group_list):
            cp.index = i
        return cp_group_list
    return inner()


def get_sub_cp_index_dict(project_id):
    SUB_CP_INDEX_DICT = {}
    if not SUB_CP_INDEX_DICT:
        sub_cp_list = get_sub_checkpoint_list(project_id)
        for i, cp in enumerate(sub_cp_list):
            SUB_CP_INDEX_DICT[cp.id] = i
    return SUB_CP_INDEX_DICT

def get_sub_checkpoint_list(project_id):
    SUB_CHECK_POINT_LIST = None
    if not SUB_CHECK_POINT_LIST:
        SUB_CHECK_POINT_LIST = list(CheckPoint.objects.filter(has_child=False, project__id=project_id))
        for i, cp in enumerate(SUB_CHECK_POINT_LIST):
            cp.index = i
    return SUB_CHECK_POINT_LIST



#根据name_abbr排序
def sort_list_by_nameabbr(list):
    list.sort(key=sort_by_name)

def sort_by_name(cp):
    """A2 return A02"""
    return '%s%s' % (cp.name_abbr[0], cp.name_abbr[1:].zfill(2))

#生成该project下的子检查点集合
def get_project_sub_cp_list(project):
    @cached('sub_cp_list_pro_%s' % str(project.id))
    def __inner():
        sub_cp_list = CheckPoint.objects.filter(has_child=False, project=project).order_by('id')
        return sub_cp_list
    return __inner()

#生成该project下的所有检查点集合
def get_project_cp_list(project):
    @cached('cp_list_pro_%s' % str(project.id))
    def __inner():
        sub_cp_list = CheckPoint.objects.filter(project=project).order_by('id')
        return sub_cp_list
    return __inner()

def get_project_cp_name_list_with_total(project, has_min_max=False):
    @cached('project_%d_cp_name_with_total_list' % project.id)
    def __inner():
        cp_name_list = ['total']
        if has_min_max:
            cp_name_list.append('max_total')
            cp_name_list.append('min_total')
        cp_list = [cp.name for cp in  get_project_cp_list(project)]
        cp_name_list.extend(cp_list)
        return cp_name_list
    return __inner()

def get_project_cp_list_with_total(project):
    cp_list = []
    total = CheckPoint()
    total.name = 'total'
    total.name_abbr = 'Total'
    total.desc = u'总得分'
    total.desc_en = 'Total Score'
    total.has_child = True
    cp_list.append(total)
    cp_list.extend(get_project_cp_list(project))
    return cp_list

def get_cp_list_by_name(cplist, project):
    cp_list = []
    for name in cplist:
        if name != 'total':
            cp = CheckPoint.objects.get(name=name, project=project)
        else:
            cp = CheckPoint()
            cp.name = 'total'
            cp.name_abbr = 'Total'
            cp.desc = u'总得分'
            cp.desc_en = 'Total Score'
            cp.has_child = True
        cp_list.append(cp)
    return cp_list

def get_brand_cp_list_by_name(cplist):
    cp_list = []
    for name in cplist:
        if name != 'total':
            cp = CheckPoint.objects.get(name=name, project__id=constant.current_project_id)
        else:
            cp = CheckPoint()
            cp.name = 'total'
            cp.name_abbr = 'Total'
            cp.desc = u'总得分'
            cp.desc_en = 'Total Score'
            cp.has_child = True
        cp_list.append(cp)
    return cp_list

def get_project_paper_resp_col_list(project):
    @cached('project_%d_paper_resp_col' % project.id)
    def __inner():
        resp_column_list = [cp.resp_col for cp in get_project_sub_cp_list(project)]
        return resp_column_list
    return __inner()

#生成该project下的计分子检查点集合(A-F)，问卷差异仅比较A－F题目
def get_project_sub_cp_score_list(project):
    @cached('sub_cp_score_list_pro_%d' % project.id)
    def __inner():
        sub_cp_list = CheckPoint.objects.filter(has_child=False, project=project).exclude(parent__name='G').order_by('id')
        return sub_cp_list
    return __inner()

def get_question_checkpoint_dict(project):
    @cached('pro_%d_question_cp_dict_by_cid' % project.id)
    def __inner():
        qustion_dict = {}
        checkpoint_list = CheckPoint.objects.filter(project=project)
        for cp in checkpoint_list:
            qustion_dict[cp.name] = cp
        return qustion_dict
    return __inner()

def get_brand_compare_cp_list(competition=False):
    @cached('brand_cp_name_abbr_list_%s'%competition)
    def __inner():
        tmp_list = ['A','B','C','D','E', 
                         'A1','A2','A3','A4','A5','A6','A7',
                         'B8','B9','B10','B11','B12','B13','B14','B15','B16','B17','B18','B19','B20','B21','B22','B23','B24',
                         'C25','C26','C27','C28','C29', 
                         'D30','D31','D32','D33','D34','D35','D36','D37','D38','D39','D40','D41','D42', 
                         'E43','E44','E45','E46', 
                         'F47','F48'];
        if competition:
            tmp_list.remove('A5')
            tmp_list.remove('A6')
            tmp_list.remove('B18')
            tmp_list.remove('B23')
            tmp_list.remove('D30')
            tmp_list.remove('D36')
            tmp_list.remove('D37')
            tmp_list.remove('D39')
            tmp_list.remove('E44')
            tmp_list.remove('E45')
            tmp_list.remove('F47')
            tmp_list.remove('F48')
        cp_list = CheckPoint.objects.filter(name_abbr__in=tmp_list, project__id=constant.current_project_id)
        total = CheckPoint()
        total.name = 'total'
        total.name_abbr = 'Total'
        total.desc = u'总得分'
        total.desc_en = 'Total Score'
        total.has_child = True
        ret = [total]
        ret.extend(cp_list)
        return ret
    return __inner()

def get_brand_question_checkpoint_dict(competition=False):
        
    @cached('pro_brand_question_cp_dict_by_cid%s'%competition)
    def __inner():
        tmp_list = ['A','B','C','D','E', 
                         'A1','A2','A3','A4','A5','A6','A7',
                         'B8','B9','B10','B11','B12','B13','B14','B15','B16','B17','B18','B19','B20','B21','B22','B23','B24',
                         'C25','C26','C27','C28','C29', 
                         'D30','D31','D32','D33','D34','D35','D36','D37','D38','D39','D40','D41','D42', 
                         'E43','E44','E45','E46', 
                         'F47','F48'];
        if competition:
            tmp_list.remove('A5')
            tmp_list.remove('A6')
            tmp_list.remove('B18')
            tmp_list.remove('B23')
            tmp_list.remove('D30')
            tmp_list.remove('D36')
            tmp_list.remove('D37')
            tmp_list.remove('D39')
            tmp_list.remove('E44')
            tmp_list.remove('E45')
            tmp_list.remove('F47')
            tmp_list.remove('F48')
        qustion_dict = {}
        checkpoint_list = CheckPoint.objects.filter(name_abbr__in=tmp_list, project__id=constant.current_project_id)
        for cp in checkpoint_list:
            qustion_dict[cp.name] = cp
        return qustion_dict
    return __inner()

def get_checkpoint_list_by_project(project):
    ck_list = CheckPoint.objects.filter(project=project).order_by('id').exclude(name='G').exclude(parent__name='G')
    return ck_list

