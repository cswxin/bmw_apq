#encoding:utf-8
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

class AuthorizedIp(models.Model):    
    createdby = models.ForeignKey(User, null=True, blank=True)
    ip = models.IPAddressField(_('Ip'))
    desc = models.CharField(u'标签', max_length=50)
    enable = models.BooleanField(_('Enable'), default=True)
    created = models.DateTimeField(_('Created'), auto_now_add=True)
    
    def __unicode__(self):
        return u'%s(%s)' % (self.desc, self.ip)
    
    class Meta:
        verbose_name = u'授权IP'
        verbose_name_plural = u'授权IP'
    
