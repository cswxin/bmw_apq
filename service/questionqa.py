#encoding:utf-8

from core import _term, _checkpoint
from survey.models import QuestionQA, Question
import constant
from mcview.decorator import cached

@cached('questionnaires')
def get_question_qa():
    current_term = _term.get_cur_term()
    areas = []
    groups = _checkpoint.get_project_cp_group_list(constant.current_project_id)
    for cp in groups:
        area = areaitem(cp.name, cp.desc)
        area.qas = _get_question_qa_by_cid(cp.name)
        area.qas.sort(lambda x, y:comparcid(x, y))
        if cp.name == 'G':
            question = Question()
            question.cid = 'G49b'
            question.title = u'有待改进的地方→'
            area.qas.insert(0, question)
            question = Question()
            question.cid = 'G49a'
            question.title = u'做得比较好的地方→'
            area.qas.insert(0, question)
            question = Question()
            question.cid = ''
            question.title = u'除了以上这些评价的问题之外，经销商的表现有没有您认为做得比较好的地方或有待改进的地方？'
            area.qas.insert(0, question)
            
        areas.append(area)
    return areas, current_term

def _get_question_qa_by_cid(keyid):
        query = QuestionQA.objects.filter(question__cid__startswith=keyid,
                            question__project__id=constant.current_project_id).order_by('question__cid')
        qas = []
        for qa in query:
            qas.append(qa)
            q = qa.question
            qa.cid = q.name_abbr #使用新题号
            qa.title = q.title
        return qas   
    
class areaitem(object):
    def __init__(self, keyid, name):
        self.keyid = keyid
        self.name = name
        self.qas = []
    
def comparcid(x, y):
    try:
        cx = int(x.cid[1:])
        cy = int(y.cid[1:])
    except ValueError:
        return 0
    return cx - cy     
