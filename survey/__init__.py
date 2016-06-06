#encoding:utf-8

import constant

#获得各个部分显示的html,respondent可能为空
def get_paper_part_html(request,part,respondent,paper=None):
    import views
    html = ''
    methodname = 'get_part_%s_html' % part
    if hasattr(views,methodname):
        func = getattr(views,methodname)
        html = func(request,respondent,paper)
    
    return html

#保存相关的respondent数据,respondent可能为空
#返回respondent对象
def save_paper_part_data(request,part,respondent,paper):
    import views
    from models import Respondent
    resp = respondent
    if not resp:
        resp = Respondent()
        resp.project_id = request.POST.get('pid',1)
        resp.user = request.user
        resp.save()
    
    methodname = 'save_part_%s_data' % part
    if hasattr(views,methodname):
        func = getattr(views,methodname)
        func(request,resp,paper)
        resp.save()
    
    return resp

