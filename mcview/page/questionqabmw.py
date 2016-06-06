#encoding:utf-8
from django.contrib.auth.decorators import login_required
from mcview.decorator import render_to
from mcview import pageman
from survey.models import QuestionQANew

@login_required
@render_to('questionqa.html')
def questionqabmw(request):
    qa_list = QuestionQANew.objects.filter(brand='BMW')
    for qa in qa_list:
        qa.child_list = QuestionQANew.objects.filter(parent=qa)
        for cqa in qa.child_list:
            cqa.child_list = QuestionQANew.objects.filter(parent=cqa)
            cqa.child_length = len(cqa.child_list)
    
    return locals()

url_list = pageman.patterns('QuestionnaireQABMW', '',
    pageman.MyUrl(None, questionqabmw, name=None),
)
