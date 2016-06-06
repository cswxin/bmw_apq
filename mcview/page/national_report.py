#encoding:utf-8
from mcview.decorator import render_to
from mcview import pageman
from service.core import _term, _document
from mc import enums
from django.contrib.auth.decorators import login_required

@login_required
@render_to('index.html')
def index(request):
    current_term = _term.get_cur_term()
    reports = _document.get_regional_report_document(current_term, enums.AREA_ALL)
    return locals()

url_list = pageman.patterns('NationalReport', '',
    pageman.MyUrl(None, index, name=None),
)
