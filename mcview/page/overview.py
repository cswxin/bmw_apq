#encoding:utf-8
from mcview.decorator import render_to
from mcview import pageman

@render_to('index.html')
def index(request):
    return locals()

url_list = pageman.patterns('ProjectOverview', '',
    pageman.MyUrl(None, index, name=None),
)
