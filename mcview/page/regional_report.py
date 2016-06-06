#encoding:utf-8
from mcview.decorator import render_to
from django.contrib.auth.decorators import login_required
from mcview import pageman
from service.core import _term, _document
from mc import enums

@login_required
@render_to('index.html')
def index(request):
    current_term = _term.get_cur_term()
    east_reports = _document.get_regional_report_document(current_term, enums.AREA_EAST)
    north_reports = _document.get_regional_report_document(current_term, enums.AREA_NORTH)
    south_reports = _document.get_regional_report_document(current_term, enums.AREA_SOUTH)
    west_reports = _document.get_regional_report_document(current_term, enums.AREA_WEST)
    return locals()

url_list = pageman.patterns('RegionalReport', '',
    pageman.MyUrl(None, index, name=None),
)
