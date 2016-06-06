#encoding:utf-8
import os, sys
from mcview.decorator import cached  
sys.path.insert(0, os.path.abspath(os.curdir))
from survey.models import Question, Alternative

def get_alt_list_exclude_a(question):
    alts = Alternative.objects.filter(question=question).exclude(cid__icontains='a').order_by('cid')
    return alts

def sortfunc(x, y):
        return  cmp(x.listorder, y.listorder);
#根据q_cid_list返回否选项的alt字典
def get_no_alts(paper, q_cid_list, extern_context):
    for q_cid in q_cid_list:
        question = Question.objects.get(project=paper.project, cid=q_cid)
        alt_list = get_alt_list_exclude_a(question)
        if question.id==184 or question.id==263:
            sorted_lists = [alt for alt in alt_list]
            sorted_lists.sort(sortfunc)
            alt_list = sorted_lists
        extern_context[q_cid] = alt_list
        
#获取0分原�
def get_zero_reason(paper, checkpoint):
    try:
        result = paper.respondent.get_data('%s__open' % checkpoint.name)
        if '98^-^' in result:
            other_ans = paper.respondent.get_data('%sother' % checkpoint.name)
            result = restore_result(checkpoint.question, result, other98=other_ans)
        else:
            result = restore_result(checkpoint.question, result)
        result_en = paper.respondent.get_translation(checkpoint.name)
    except:
        result = '-'
        result_en = '-'
    return result or '-', result_en or '-'

def restore_result(question, result, hasAltCid=False, other98=''):
    if result is None: 
        return None
    sp = '^-^'
    ans = []
    if sp in result:
        temps = result.split(sp)
        altlen = len(temps)
        cid_list = list(temps)
        cid_list.remove(cid_list[len(cid_list) - 1])
        for cid in cid_list:
            alt = Alternative.objects.get(question=question, cid=cid)
            if hasAltCid:
                if other98 and '98' == alt.cid:
                    ans.append('%s.%s(%s)' % (alt.cid, alt.title, other98))
                else:
                    ans.append('%s.%s' % (alt.cid, alt.title))
            else:
                if other98 and '98' == alt.cid:
                    ans.append('%s(%s)' % (alt.title, other98))
                else:
                    ans.append(alt.title)
        ans.append(temps[altlen - 1])
        return '<br>'.join(ans)
    else:
        return result

def get_question_dict(project):
    @cached('question_cid_dict_by_pro_%d' % project.id)
    def __inner():
        qustion_dict = {}
        question_list = Question.objects.filter(project=project)
        for q in question_list:
            qustion_dict[q.cid] = q
        return qustion_dict
    return __inner()

def get_question_by_cid(project, cid):
    return get_question_dict(project).get(cid)

if __name__ == "__main__":
    question = Question.objects.get(id='153')
    print get_alt_list_exclude_a(question)
