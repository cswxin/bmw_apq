#encoding:utf-8
from django.contrib.auth.decorators import login_required
from mcview.decorator import render_to
from mcview import pageman
from survey.models import QuestionQANew
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.shortcuts import HttpResponse
from django.utils import simplejson

@login_required
@render_to('index.html')
def questionqa(request):
    cp_score_list = ['Q4a', 'Q7a', 'Q8a', 'Q9a', 'Q11a', 'Q12a', 'Q13a', 'Q16a', 'Q34a', 'Q35a', 'Q43a', 'Q44a', 'Q46a']
    cp_no_score_list = ['Q4b', 'Q4c', 'Q4d', 'Q4e', 'Q7b', 'Q8b', 'Q9b', 'Q11b', 'Q12b', 'Q12c', 'Q12d', 'Q12e', 'Q12f', 'Q12g', 'Q12h', 'Q12i', 'Q13b', 'Q13c', 'Q13d', 'Q16b', 'Q16c', 'Q16d', 'Q34b', 'Q35b', 'Q35c', 'Q43b', 'Q43c', 'Q44b', 'Q46b']
    cp_score_dict = {'Q4a':10, 'Q7a':10, 'Q8a':4, 'Q9a':4, 'Q11a':6, 'Q12a':17, 'Q13a':12, 'Q16a':12, 'Q34a':10, 'Q35a':9, 'Q43a':9, 'Q44a':10, 'Q46a':6}

    qa_list = QuestionQANew.objects.filter(brand='BMW_2015')
    for qa in qa_list:
        qa.child_list = QuestionQANew.objects.filter(parent=qa)
        for cqa in qa.child_list:
            cqa.qid = 'Q%s' % cqa.number
            cqa.child_list = QuestionQANew.objects.filter(parent=cqa)
            cqa.child_length = len(cqa.child_list)
            cqa.rowspan = cp_score_dict.get(cqa.qid)
    return locals()

@login_required
@csrf_exempt
def questionqa_change(request):
    sdicts = {}

    cp_score_list = ['Q4a', 'Q7a', 'Q8a', 'Q9a', 'Q11a', 'Q12a', 'Q13a', 'Q16a', 'Q34a', 'Q35a', 'Q43a', 'Q44a', 'Q46a']
    cp_no_score_list = ['Q4b', 'Q4c', 'Q4d', 'Q4e', 'Q7b', 'Q8b', 'Q9b', 'Q11b', 'Q12b', 'Q12c', 'Q12d', 'Q12e', 'Q12f', 'Q12g', 'Q12h', 'Q12i', 'Q13b', 'Q13c', 'Q13d', 'Q16b', 'Q16c', 'Q16d', 'Q34b', 'Q35b', 'Q35c', 'Q43b', 'Q43c', 'Q44b', 'Q46b']
    cp_score_dict = {'Q4a':10, 'Q7a':10, 'Q8a':4, 'Q9a':4, 'Q11a':6, 'Q12a':17, 'Q13a':12, 'Q16a':12, 'Q34a':10, 'Q35a':9, 'Q43a':9, 'Q44a':10, 'Q46a':6}

    type_id = request.POST.get('type_id')
    if type_id == '1':
        qa_list = QuestionQANew.objects.filter(brand='BMW')
    if type_id == '2':
        qa_list = QuestionQANew.objects.filter(brand='MINI')
    if type_id == '3':
        qa_list = QuestionQANew.objects.filter(brand='BMW_2015')
    if type_id == '4':
        qa_list = QuestionQANew.objects.filter(brand='MINI_2015')
    for qa in qa_list:
        qa.child_list = QuestionQANew.objects.filter(parent=qa)
        for cqa in qa.child_list:
            cqa.qid = 'Q%s' % cqa.number
            cqa.child_list = QuestionQANew.objects.filter(parent=cqa)
            cqa.child_length = len(cqa.child_list)
            cqa.rowspan = cp_score_dict.get(cqa.qid)

    template_file = "questionqa/contentDiv.html"
    ret = locals()
    html = render_to_string(template_file, ret)
    sdicts['html'] = html
    return HttpResponse(simplejson.dumps(sdicts, ensure_ascii=False))

url_list = pageman.patterns('QuestionnaireQA', '',
    pageman.MyUrl(None, questionqa, name=None),
    pageman.MyUrl('change', questionqa_change, name='questionqa_change'),
)
