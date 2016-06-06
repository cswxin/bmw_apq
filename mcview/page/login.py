#encoding:utf-8
from mcview.decorator import render_to
from service import login

@render_to('index.html')
def index(request):
    return login.index(request)

@render_to('changepassword.html')
def change_password(request):
    return login.change_password(request)

def logout(request):
    return login.logout(request)

from django.conf.urls.defaults import patterns,url

url_list = patterns('',
    url(r'^$', index,name="index"),
    url(r'^logout/$',logout,name="logout"),
    url(r'^ChangePassword/$',change_password,name="ChangePassword"),
)
