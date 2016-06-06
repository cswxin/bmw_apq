#encoding:utf-8

from django.contrib.auth.models import User
from models import LoginLogout

class IPMiddleware(object):
    def process_request(self, request):
        pass
    
    def process_response(self, request, response):
        if hasattr(request,'user'):
            user = request.user
            if user.is_authenticated():
                ls = LoginLogout.objects.filter(user=user,type=0)
                if len(ls) > 0:
                    l = ls[0]
                    remoteip  = request.META['REMOTE_ADDR']
                    l.ip = remoteip
                    l.type = 1
                    l.save()
        
        return response
