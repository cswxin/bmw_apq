#encoding:utf-8
from django.shortcuts import HttpResponseRedirect
from django.contrib import auth
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from verifier import myvalidate
from core import _term, _user
from mcview.decorator import cached

'''
    login, user缓存刷新
'''
def index(request):
    if request.method == 'POST':
        username = request.POST.get('username', None).strip()
        password = request.POST.get('password', None).strip()
        validatepath = request.POST.get('fstamp', None)
        vcode = request.POST.get('VerifyCode', None)
        if None in [username, password, validatepath, vcode]:
            errormsg = u'缺少参数！'
            register_pic = myvalidate.generateVadImage()
            return locals()
        if not myvalidate.verify(validatepath, vcode):
            errormsg = u'验证码错误！'
            register_pic = myvalidate.generateVadImage()
            return locals()
        
        @cached('user_key_%s' % (username))
        def _login(username, password, refresh=True):
            return auth.authenticate(username=username, password=password)
        
        user = _login(username, password, refresh=True)
        if user is not None and user.is_active:
            auth.login(request, user)
            next = request.REQUEST.get('next', None)
            if next:
                return HttpResponseRedirect(next)
            else:
#                from userpro import enums
#                if _user.check_user_in_dealer_group(request.user) and  _user.has_dealer_page_perm(request.user):
#                    return HttpResponseRedirect(reverse('DealerReport/dealeranalysis'))
                return HttpResponseRedirect(reverse('ProjectOverview'))
        else:
            errormsg = u"登录失败！"
            infos = ''
            if user is None:
                infos = u'user is None'
            else:
                infos = u'user is inactive'
            register_pic = myvalidate.generateVadImage()
            return locals()
    else:
        if request.user.is_authenticated():
#            from userpro import enums
#            if _user.check_user_in_dealer_group(request.user) and  _user.has_dealer_page_perm(request.user):
#                return HttpResponseRedirect(reverse('DealerReport/dealeranalysis'))
            return HttpResponseRedirect(reverse('ProjectOverview'))
        else:
            register_pic = myvalidate.generateVadImage()
            return locals()

    
@login_required
def change_password(request):
    current_term = _term.get_cur_term()
    if request.method == "POST":
        username = request.user
        oldpassword = request.POST.get('oldpassword', None).strip()
        password = request.POST.get('password', None).strip()
        confirmpass = request.POST.get('confirmpass', None).strip()
        if None in [username, oldpassword, confirmpass]:
            message = u"参数错误！"
            return locals()
        if password != confirmpass:
            message = u"两次输入密码不匹配！"
            return locals()
        userinfo = User.objects.get(username=username)
        if not userinfo:
            message = u"未知用户！"
            return locals()
        if not userinfo.check_password(oldpassword):
            message = u"原始密码错误！"
            return locals()
        else:
            userinfo.set_password(password)
            userinfo.save()
            message = u"成功修改密码！"
            return locals()
    else:
        return locals()
    
@login_required
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('index'))
