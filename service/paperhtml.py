#encoding:utf-8
from django.shortcuts import HttpResponse, HttpResponseRedirect, render_to_response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from survey.models import Question, Alternative, Respondent, Project
from survey.q_models import get_q_model
from service.core._user import has_tran_perm, has_manage_perm
from service.core._question import get_no_alts
from service.core._common import changeTupleValue

QUESTION_DICT = {}
ALTERNATIVE_DICT = {}
extern_context = {}

def save_radio_data(request, respondent, q_cid_list):
    '''
    save_radio_data处理单选数据
    @param request:HTTP request请求
    @param respondent: respondent对象
    @param q_cid_list:单选字段组成的list
    '''
    pid = respondent.project_id
    tran_perm = has_tran_perm(request.user)
    manage_perm = has_manage_perm(request.user)
    for q_cid in q_cid_list:
        alt_cid = request.POST.get(q_cid, '').strip()
        question = QUESTION_DICT.get((pid, q_cid))
        if not question:
            question = Question.objects.get(project=pid, cid=q_cid)
            QUESTION_DICT[(pid, question.cid)] = question
        alt = ALTERNATIVE_DICT.get((pid, q_cid, alt_cid))
        if not alt:
            alt = Alternative.objects.get(question=question, cid=alt_cid)
            ALTERNATIVE_DICT[(pid, q_cid, alt_cid)] = alt
    
        q_model = get_q_model(question)
        tran_content = request.POST.get('%s__open__EN' % q_cid, '')
        if alt.open:
                open_content = request.POST.get('%s__open' % q_cid, '')
                q_model.set_answer(respondent.id, [alt.id, open_content])
        else:
            q_model.set_answer(respondent.id, alt.id)
        if manage_perm and tran_content:
            tran_content = request.POST.get('%s__open__EN' % q_cid, '')
            respondent.set_translation(q_cid, tran_content)
        if tran_perm:
            respondent.set_translation(q_cid, tran_content)
            
                
def save_blank_data(request, respondent, q_cid_list):
    '''
    save_blank_data处理填空数据
    @param request:HTTP request请求
    @param respondent: respondent对象
    @param q_cid_list:填空字段组成的list
    '''
    pid = respondent.project_id
    tran_perm = has_tran_perm(request.user)
    manage_perm = has_manage_perm(request.user)
    dealer_code = ''
    for q_cid in q_cid_list:
        answer = request.POST.get(q_cid) or request.POST.getlist(q_cid)[0]
        #上面or部分只是为了绕过自动测试的BUG,让自动测试可以通过
        
        if respondent.project_id == 3:
            #MINI 问卷时检查dealer_code并做修改
            if 'dealer_code' == q_cid and not answer.endswith('_M'):
                answer = '%s_M' % answer
                dealer_code = answer
            if 'survey_code' == q_cid and answer.find(dealer_code) == -1:
                answer = answer.replace(dealer_code[:-2], dealer_code)
        
        question = QUESTION_DICT.get(q_cid)
        if not question:
            question = Question.objects.get(project=pid, cid=q_cid)
            QUESTION_DICT[(pid, question.cid)] = question
        tran_content = request.POST.get('%s__EN' % q_cid, '')
        if tran_perm and tran_content:
            respondent.set_translation(q_cid, tran_content)
        else:
            q_model = get_q_model(question)
            q_model.set_answer(respondent.id, answer)
            if manage_perm and tran_content:
                respondent.set_translation(q_cid, tran_content)
                
def save_multiple_blank_data(request, respondent, q_cid_dict):
    pid = respondent.project_id
    tran_perm = has_tran_perm(request.user)
    manage_perm = has_manage_perm(request.user)
    for cid in q_cid_dict.keys():
        answer = []
        answer_en = {}
        for q in q_cid_dict[cid]:
            q_cid = cid + "_" + q
            data = request.POST.get(q_cid)
            answer.append(data)
            data_en = request.POST.get(q_cid + '__EN', None)
            if data_en:
                answer_en[q_cid] = data_en
        question = QUESTION_DICT.get(cid)
        if not question:
            question = Question.objects.get(project=pid, cid=cid)
            QUESTION_DICT[(pid, question.cid)] = question
        if tran_perm and len(answer_en):
            respondent.set_translations(answer_en)
        else:
            q_model = get_q_model(question)
            q_model.set_answer(respondent.id, answer)
            if manage_perm:
                respondent.set_translations(answer_en)

def save_multiple_score_data(request, respondent, q_cid_dict):
    pid = respondent.project_id
    answer = []
    for cid in q_cid_dict.keys():
        for q in q_cid_dict[cid]:
            q_cid = cid + "_" + q
            data = request.POST.get(q_cid)
            answer.append(int(data))
        question = QUESTION_DICT.get(cid)
        if not question:
            question = Question.objects.get(project=pid, cid=cid)
            QUESTION_DICT[(pid, question.cid)] = question
        
        q_model = get_q_model(question)
        q_model.set_answer(respondent.id, answer)

def get_part_basic_html(request, respondent, paper):
    from mc import get_term_by_respondent, get_audit_history
    term = get_term_by_respondent(respondent)
    audits = get_audit_history(respondent)
    
    extern_context['term'] = term
    extern_context['audits'] = audits
    extern_context['user'] = request.user
    extern_context['paper'] = paper
    return _render_html(request, respondent, 'survey/survey_part_basic.html', extern_context=extern_context)

def get_part_a_html(request, respondent, paper):
    extern_context['paper'] = paper
    q_cid_list = ['A3', 'A52a', 'A6']
    if paper.project.id == 4:
        q_cid_list = ['A3', 'A6']
    get_no_alts(paper, q_cid_list, extern_context)
    return _render_html(request, respondent, 'survey/survey_part_A.html', extern_context=extern_context, q_cid_list=q_cid_list)

def get_part_b_html(request, respondent, paper):
    extern_context['paper'] = paper
    q_cid_list = ['B7a', 'B8', 'B11a', 'B12', 'B14a', 'B21a', 'B20', 'B23', 'B60']
    if paper.project.id == 4:
        q_cid_list = ['B7a', 'B8', 'B11a', 'S2', 'B20', 'B23']
    get_no_alts(paper, q_cid_list, extern_context)
    return _render_html(request, respondent, 'survey/survey_part_B.html', extern_context=extern_context, q_cid_list=q_cid_list)

def get_part_c_html(request, respondent, paper):
    extern_context['paper'] = paper
    q_cid_list = ['C24', 'C25']
    get_no_alts(paper, q_cid_list, extern_context)
    return _render_html(request, respondent, 'survey/survey_part_C.html', extern_context=extern_context, q_cid_list=q_cid_list)

def get_part_d_html(request, respondent, paper):
    extern_context['paper'] = paper
    q_cid_list = ['D41a', 'D63', 'D43']
    if paper.project.id == 3:
        q_cid_list = ['D41a', 'T1', 'D43']
    if paper.project.id == 4:
        q_cid_list = ['D43', ]
    get_no_alts(paper, q_cid_list, extern_context)
    return _render_html(request, respondent, 'survey/survey_part_D.html', extern_context=extern_context, q_cid_list=q_cid_list)

def get_part_e_html(request, respondent, paper):
    extern_context['paper'] = paper
    q_cid_list = ['E44', 'E46', 'E47']
    if paper.project.id == 4:
        q_cid_list = ['E44', 'E47']
    get_no_alts(paper, q_cid_list, extern_context)
    return _render_html(request, respondent, 'survey/survey_part_E.html', extern_context=extern_context, q_cid_list=q_cid_list)

def get_part_f_html(request, respondent, paper):
    extern_context['paper'] = paper
    q_cid_list = []
    if paper.project.id != 4:#竞品问卷没有F检查点
        q_cid_list = ['F48', ]
        get_no_alts(paper, q_cid_list, extern_context)
    return _render_html(request, respondent, 'survey/survey_part_F.html', extern_context=extern_context, q_cid_list=q_cid_list)

def get_part_g_html(request, respondent, paper):
    extern_context['paper'] = paper
    return _render_html(request, respondent, 'survey/survey_part_G.html', extern_context=extern_context)

def get_part_n_html(request, respondent, paper):
    extern_context['paper'] = paper
    return _render_html(request, respondent, 'survey/survey_part_N.html', extern_context=extern_context)

def get_part_h_html(request, respondent, paper):
    extern_context['paper'] = paper
    import mc
    if mc.is_q3(paper):
        extern_context = {}
        import mc
        questions = mc.get_h3_question()
        extern_context['questions'] = questions
        return _render_html(request, respondent, 'survey/survey_part_H3.html', extern_context=extern_context)
    else:
        return _render_html(request, respondent, 'survey/survey_part_H.html', extern_context=extern_context)

def _render_html(request, respondent, templatename, extern_context={}, q_cid_list=[]):
    from django.template.loader import render_to_string
    if respondent is None:
        answers = None
        trans_contents = None
    else:
        answers = respondent.answers
        trans_contents = respondent.get_translations()
    tran_perm = int(has_tran_perm(request.user))
    manage_perm = int(has_manage_perm(request.user))
    
    cid_dict = {}
    for q_cid in q_cid_list:
        if answers[q_cid][0] == 'A2':
            if answers[q_cid][1]:
                alts = answers[q_cid][1].split('^-^')
                altlen = len(alts)
                alt_list = []
                temp_list = list(alts)
                temp_list.remove(temp_list[len(temp_list) - 1])
                for a in temp_list:
                    alt_list.append('%s' % int(a))
                answers[q_cid] = changeTupleValue(answers[q_cid], answers[q_cid][1], alts[altlen - 1])
                cid_dict[q_cid] = ','.join(alt_list)
    extern_context['alt_ans'] = cid_dict
    
    cid_list = []
    questions = extern_context.get('questions', [])
    for q in questions:
        #增加补充说明
        addon_cid = '%s__addon' % q.cid
        
        if answers:
            an = answers.get(q.cid, None)
            if an:
                q.answer0 = an[0]
                q.answer1 = an[1]
            an = answers.get(addon_cid, None)
            if an:
                q.addon = an
        
        if trans_contents:
            tran = trans_contents.get(q.cid, None)
            q.trans_contents = tran
            
            tran = trans_contents.get(addon_cid, None)
            q.addon_en = tran
        
        cid_list.append(q.cid.encode('utf-8'))
    
    extern_context['question_cid_list'] = cid_list
    
    paper = extern_context.get('paper', None)
    if paper:
        project_id = paper.project.id
    else:
        project_id = request.GET.get('project_id', 2) #获得项目id 默认为宝马项目
    project = Project.objects.get(id=project_id)
    
    info_data = {'respondent':respondent, 'answers':answers, 'tran_perm':tran_perm, 'manage_perm':manage_perm, 'trans_contents':trans_contents, 'project':project}
    info_data.update(extern_context)
    html = render_to_string(templatename, info_data)
    return html

def save_part_basic_data(request, respondent, paper):
    #处理填空题
    q_cid_list = [
        'customer_code',
        'dealer_code',
        'appraiser_code',
        'survey_code',
        'consultant_name',
        'booking_date',
        'booking_begin_time',
        'booking_end_time',
        'visit_date',
        'visit_begin_time',
        'visit_end_time',
        'visitor_numb',
        'customer_name',
        'customer_address',
        'term_id'
    ]
    save_blank_data(request, respondent, q_cid_list)
    
    #处理单选题
    q_cid_list = ['consultant_sex', 'service_type', 'car_type', 'at_mt']
    save_radio_data(request, respondent, q_cid_list)

def save_part_a_data(request, respondent, paper):
    q_cid_list = ['A1a', 'A2', 'A4', 'A3', 'A52a', 'A5', 'A6']
    if paper.project.id == 4:
        q_cid_list = ['A1a', 'A2', 'A4', 'A3', 'A6']
    save_radio_data(request, respondent, q_cid_list)

def save_part_b_data(request, respondent, paper):
    q_cid_list = ['B7a', 'B8', 'B9', 'B11a', 'B10', 'B12', 'B14a', 'B15', 'B16', 'B18', 'B21a', 'B20', 'B22', 'B19', 'B23', 'B60', 'B61']
    if paper.project.id == 4:
        q_cid_list = ['B7a', 'B8', 'B9', 'B11a', 'B10', 'S1', 'S2', 'B15', 'B16', 'B18', 'B20', 'B22', 'B19', 'B23', 'B61']
    save_radio_data(request, respondent, q_cid_list)
    q_cid_list = ['consultant_name', 'visit_date', 'visit_begin_time', 'estimate_finish_date', 'estimate_finish_time', 'estimate_price', 'B8other', 'B21aother', 'B60other']
    if paper.project.id == 4:
        q_cid_list = ['consultant_name', 'visit_date', 'visit_begin_time', 'estimate_finish_date', 'estimate_finish_time', 'estimate_price', 'B8other']
    save_blank_data(request, respondent, q_cid_list)

def save_part_c_data(request, respondent, paper):
    q_cid_list = ['repare_finish_date', 'repare_finish_time', 'C24other', 'C25other']
    save_blank_data(request, respondent, q_cid_list)
    q_cid_list = ['C24', 'C25', 'C26', 'C28', 'C29']
    save_radio_data(request, respondent, q_cid_list)

def save_part_d_data(request, respondent, paper):
    q_cid_list = ['D30', 'D31', 'D32', 'D33', 'D35', 'D37', 'D62', 'D36', 'D41a', 'D63', 'D40a', 'D42', 'D43']
    if paper.project.id == 3:
        q_cid_list = ['D30', 'D31', 'D32', 'D33', 'D35', 'D37', 'D62', 'D36', 'D41a', 'T1', 'T2', 'D42', 'D43']
    if paper.project.id == 4:
        q_cid_list = ['D31', 'S3', 'S4', 'D35', 'D37', 'S5', 'S6', 'D42', 'D43']
    save_radio_data(request, respondent, q_cid_list)
    q_cid_list = ['final_price', 'D41aother', 'D63other']
    if paper.project.id == 3:
        q_cid_list = ['final_price', 'D41aother']
    if paper.project.id == 4:
        q_cid_list = ['final_price', ]
    save_blank_data(request, respondent, q_cid_list)

def save_part_e_data(request, respondent, paper):
    q_cid_list = ['E44', 'E45', 'E46', 'E47']
    if paper.project.id == 4:
        q_cid_list = ['E44', 'E47']
    save_radio_data(request, respondent, q_cid_list)
    q_cid_list = ['E46other', 'E47other']
    if paper.project.id == 4:
        q_cid_list = ['E47other', ]
    save_blank_data(request, respondent, q_cid_list)

def save_part_f_data(request, respondent, paper):
    q_cid_list = ['F48', 'F49']
    save_radio_data(request, respondent, q_cid_list)
    q_cid_dict = {'F49a':['A1', 'A2', 'A3', 'A4'], 'F49b':['A1', 'A2', 'A3', 'A4'], 'F49c':['A1', 'A2', 'A3', 'A4'], 'F49d':['A1', 'A2', 'A3', 'A4']}
    save_multiple_blank_data(request, respondent, q_cid_dict)

def save_part_g_data(request, respondent, paper):
    q_cid_dict = {'G51':['A1']}
    save_multiple_score_data(request, respondent, q_cid_dict)
    q_cid_dict = {'G50':['A1', 'A2']}
    save_multiple_blank_data(request, respondent, q_cid_dict)
    if paper.project.id == 2:
        q_cid_list = ['G64', ]
        save_radio_data(request, respondent, q_cid_list)
    if paper.project.id == 3:
        q_cid_list = ['T3', ]
        save_blank_data(request, respondent, q_cid_list)

#第三期新加部分
def save_part_n_data(request, respondent, paper):
    q_cid_list = ['A52', 'B53', 'C54', 'E55']
    save_radio_data(request, respondent, q_cid_list)
    
def save_part_h_data(request, respondent, paper):
    import mc
    if mc.is_q3(paper):
        from tools.add_q3_question import question_list
        q_cid_list = []
        for cid, qname in question_list[4:]:
            q_cid_list.append(cid)
        save_radio_data(request, respondent, q_cid_list)
        
        blank_cid_list = ['%s__addon' % cid for cid in q_cid_list]
        save_blank_data(request, respondent, blank_cid_list)
    else:
        q_cid_list = ['H12', 'H15', 'H16', 'H17', 'H21', 'H27', 'H36', 'H43', 'H46', 'H47']
        save_radio_data(request, respondent, q_cid_list)
