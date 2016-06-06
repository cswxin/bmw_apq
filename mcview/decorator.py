#encoding=utf-8

from django.shortcuts import render_to_response

from django.template import RequestContext
from django.core.cache import cache

from service.core import _user

''' cache result by key, 24*60*60 or nerver expired
        the result can be anything: truple, dict, list, etc
    '''

def cached (cache_key, timeout=24 * 60 * 60 * 60):
    def cached (function):
        def wrapper(*args, **kwargs):
            refresh = False
            if kwargs.has_key('refresh'):
                refresh = kwargs['refresh']
            if not refresh:
                result = cache.get(cache_key)
            if refresh or result is None:
                result = function(*args, **kwargs)
                if result:
#                    if isinstance(result, dict):
#                        raise Exception(u'@cached decorator accept the function only 1 result returned')
#                    else:
                    cache.set(cache_key, result, timeout)
            #对于cache中已经存在的对象，可能会添加属性，这里用attrs来指出cache的对象是否已经存在该属性，若没有，则执行function
            #切记，function的返回值必须是该对象
            #attrs支持数组，及单个属性            
            if kwargs.has_key('attrs'):
                attrs = kwargs['attrs']
                existed = False
                if isinstance(attrs, (list, tuple)):
                    for attr in attrs:
                        existed = hasattr(result, attr)
                        if existed == False:
                           break
                elif isinstance(attrs, str):
                    existed = hasattr(result, attrs)
                
                if existed == False:
                    result = function(*args, **kwargs)
                    if result:
                        cache.set(cache_key, result, timeout)
            
            return result
        return wrapper
    return cached

def get_cache(cache_key):
    return cache.get(cache_key)

#诡异现象：此代码若直接放在wrapper体内，则template值为undefine！！！
#context属性由pageman，init_urls加载模块时动态注入
def htmls(function, t):
    import inspect
    template = t
    m = inspect.getmodule(function)
    if hasattr(m, 'folder') :
        context = getattr(m, 'folder')
        template = '%s/%s' % (context, t)
    return template

def render_to(template):
    def renderer(function):
        def wrapper(request, *args, **kwargs):
            output = function(request, *args, **kwargs)
            if not isinstance(output, dict):
                return output
            tmpl = output.pop('TEMPLATE', template)
            tmpl = htmls(function, tmpl)
            import page_info
            import pageman
            menuwidth = 800
            if request.user.is_authenticated():
                menus = pageman.get_menus(request)
                req_path = request.path
                
                if len(menus):
                    menuwidth = 900 / len(menus)
                    if menuwidth > 160:
                        menuwidth = 160
                #TODO: 权限判断
                has_dealer_perm = _user.has_dealer_page_perm(request.user)
                output['has_dealer_perm'] = has_dealer_perm
                
                output['menus'] = menus
                output['menuwidth'] = menuwidth
            
            output['project_style'] = page_info.project_style
            output['project_title'] = page_info.project_title
            if request.user.is_authenticated():
                has_all_page_perm = _user.has_all_page_perm(request.user)
                output['has_all_page_perm'] = has_all_page_perm
            return render_to_response(tmpl, output, context_instance=RequestContext(request))
        return wrapper
    return renderer
