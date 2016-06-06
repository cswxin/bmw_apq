#encoding:utf-8

import page_info
from django.utils.importlib import import_module
from django.conf.urls.defaults import url
from django.core.urlresolvers import RegexURLPattern
from service.core import _user
#This module converts requested URLs to callback view functions.
#    RegexURLResolver is the main class here. Its resolve() method takes a URL (as
#    a string) and returns a tuple in this format:
#    
#    (view_function, function_args, function_kwargs)


#初始化页面的url链接
def init_urls():
    url_list = []
    
    #判断是否有登录页面，如果没有，则使用默认登录页面
    loginmodule = 'mcview.page.login'
    if hasattr(page_info, 'loginpage'):
        loginmodule = page_info.loginpage
    
    m = import_module(loginmodule)
    urls = m.url_list
    url_list.extend(urls)
    
    #扫描页面
    for page in page_info.page_list:
        module_list = page[2]
        html_path_prefix = None
        if len(page) > 5:
            html_path_prefix = page[5]
        url_path_prefix = None
        if len(page) > 6:
            url_path_prefix = page[6]
        for module_name in module_list:
            m = import_module(module_name)
            if html_path_prefix:
                m.__setattr__("folder", html_path_prefix)
            if url_path_prefix:
                m.__setattr__("context", url_path_prefix)
            urls = m.url_list
            url_list.extend(urls)
    
    return url_list

class menuitem():
    def __init__(self):
        self.name_cn = ''
        self.name_en = ''

def patterns(urlprefix, prefix='', *args):
    pattern_list = []
    for t in args:
        u = t
        if isinstance(t, (list, tuple)):
            u = url(prefix=prefix, *t)
        elif isinstance(t, MyUrl):
            u = t.mapping(urlprefix, prefix=prefix)
            u.add_prefix(prefix)
        elif isinstance(u, RegexURLPattern):
            u.add_prefix(prefix)
        if u:
            pattern_list.append(u)
        else:
            raise Exception('load url mapping error %s ' % t)
    return pattern_list

class MyUrl(object):
    def __init__(self, regexstr, callback, default_args=None, name=None):
        self.regexstr = regexstr
        if callable(callback):
            self._callback = callback
        else:
            self._callback = None
            self._callback_str = callback
        self.default_args = default_args or {}
        self.name = name
        
    def mapping(self, module_urls_prefix, prefix=''):   
        tregex = r'^%s/$' % module_urls_prefix
        if self.regexstr:
            tregex = r'^%s/%s$' % (module_urls_prefix, self.regexstr)
        tname = "%s" % module_urls_prefix
        if self.name: 
            tname = "%s/%s" % (module_urls_prefix, self.name)
        return url(tregex, self._callback, self.default_args, tname, prefix)

#获得菜单集合
def get_menus(request):
    menus = []
    
    user = request.user
    pname = request.path
    
    #依据不同的用户显示不同的菜单组合
    can_show_pages = get_user_pages(user)
    
    for page in page_info.page_list:
        if page[0] not in can_show_pages:
            continue
        
        item = menuitem()
        item.name_cn = page[0]
        item.name_en = page[1]
        
        menus.append(item)
        is_active = False
        module_list = page[2]
        
        firstname = ''
        for module_name in module_list:
            m = import_module(module_name)
            urls = m.url_list
            for u in urls:
                if pname.find(u.name) >= 0:
                    is_active = True
                    break
            if not firstname:
                firstname = '/%s' % urls[0].name
        
        item.url = firstname
        item.is_active = is_active
    
    return menus

#获得用户能够查看的页�
def get_user_pages(user):
    permnames = []
    for pername in _user.get_user_perms(user):
        permnames.append(pername)
    
    pages = []
    
    for page in page_info.page_list:
        key = page[0]
        
        allowed_perms = page[3]
        disabled_perms = page[4]
        
        can_show = False
        
        #可访问权限检查，有，显示
        if allowed_perms:
            for gname in allowed_perms:
                if gname in permnames:
                    can_show = True
                    if key not in pages:
                        pages.append(key)
                        
        #不可访问权限检查，若有，则最终不能显示
        if disabled_perms:
            for gname in disabled_perms:
                if gname in permnames:
                    can_show = False
                    break
            
        if not can_show: #最终不能显示，已加入的模块剔除
            if key  in pages:
                pages.remove(key)
        elif key not in pages:
            pages.append(key)
        
    return pages
