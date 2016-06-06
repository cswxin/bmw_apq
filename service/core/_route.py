#encoding:utf-8

from mc.models import Router
from mcview.decorator import cached

@cached("terms") 
def getTerms():
    routers = Router.objects.all().order_by('-term__id') #flat=True,返回的是普通列表
    ret = []
    for r in routers:
        if r.term not in ret:
            ret.append(r.term) 
    return ret #set()去除[]中重复的元素


def getRoutesInfo(term_id):
#    @cached('routesInfo%s'%term_id)
    def _inner():
        routers = Router.objects.filter(term=term_id).order_by('id')  
        return routers
    return _inner()

def updateRouter(router_id, user_id):
    router_update = Router.objects.filter(id=router_id).update(user=user_id)

    return router_update

#def ajaxGetTerm():
#    pass
