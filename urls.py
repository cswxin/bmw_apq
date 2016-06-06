#encoding:utf-8
from django.conf.urls.defaults import patterns, url, include
from mcview import views as mcv
from mc import views as mv
import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
                       
    url(r'^SuperReport/$', mcv.super_report, name="SuperReport"),
    url(r'^functionlist/$', mv.functionlist),
    url(r'^trans_export_need/$', mv.trans_export_need),
    url(r'^trans_export_all/$', mv.trans_export_all),
    url(r'^trans_import/$', mv.trans_import),
    
    url(r'^orignial_export/(?P<term_id>\d+)/$', mv.orignial_export),
    url(r'^score_export/(?P<term_id>\d+)/$', mv.score_export),
    url(r'^submitpaper/$', mv.submit_paper_req),
    url(r'^genreport/$', mv.gen_report_req),
    url(r'^aggregatereport/$', mv.aggregate_report),
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_STATIC_PATH}),
    url(r'^file/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    
    (r'^admin/', include(admin.site.urls)),
)

from mcview.pageman import init_urls
url_list = init_urls()

urlpatterns.extend(url_list)
