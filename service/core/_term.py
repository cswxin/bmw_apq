#encoding:utf-8
from mc.models import Term
from mcview.decorator import cached

@cached ("current_term")
def get_cur_term():
    query = Term.objects.filter(is_active=True).order_by('-id')
    if query.count() > 0:
        current_term = query[0]
    else:
        current_term = Term.objects.all().order_by('-id')[:1][0]
    return current_term

def get_2012_all_terms():
    terms = Term.objects.filter().order_by('id')
    return terms

@cached ("current_term")
def set_cur_term(term, refresh=False):
    return term

@cached ("current_input_term")
def get_cur_input_term():
    query = Term.objects.filter(is_active_input=True).order_by('-id')
    if query.count() > 0:
        current_input_term = query[0]
    else:
        current_input_term = Term.objects.all().order_by('-id')[:1][0]
    return current_input_term

@cached ("current_input_term")
def set_cur_input_term(term, refresh=False):
    return term

#或获得当前期数以前的列表(2012年)
def get_list_terms(current_term):
    query = Term.objects.filter(id__lte=current_term.id)
    return query

def get_2012_farward_term_list(current_term_id):
    query = Term.objects.filter(id__lte=current_term_id)
    return query


def getDefaultTerm(term_name):
    query = Term.objects.filter(name=term_name).values("id")

    return query
    
def get_term_by_id(term_id):
    try:
        term = Term.objects.get(id=term_id)
        return term
    except:
        return None

def get_all_terms():
    query = Term.objects.all()
    return query

def get_terms(current_term=None):
    '''期数查询接口，返回值为所有期的queryset'''
    if not current_term:
        return Term.objects.all().order_by('id')
    else:
        return Term.objects.filter(id__lte=current_term.id).order_by('id')
