#encoding:utf-8

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from mc.models import Dealer

class LoginLogout(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    ip = models.IPAddressField(_('Ip'), null=True, blank=True)
    type = models.IntegerField(_('Type'), default=0)
    created = models.DateTimeField(_('Created'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Login Logout')

#登入记录
def record_login(sender, **kwargs):
    user = kwargs['instance']
    import datetime
    now = datetime.datetime.now()
    dt = datetime.timedelta(seconds=2)
    if user.last_login > user.date_joined + dt and user.last_login + dt > now:
        l = LoginLogout(user=user)
        l.save()
        
        up, create = UserProfile.objects.get_or_create(user=user)
        up.login_count += 1
        up.save()
    
post_save.connect(record_login, sender=User, dispatch_uid='userpro.login')

class UserPermission(models.Model):
    name = models.CharField(_('name'), max_length=50)
    
    class Meta:
        verbose_name = _('permission')
    
    def __unicode__(self):
        return unicode(self.name)

class UserProfile(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    login_count = models.IntegerField(_('Login Count'), null=True, blank=True, default=0)
    user_permissions = models.ManyToManyField(UserPermission, verbose_name=_('user permissions'), blank=True)
    dealer = models.ForeignKey(Dealer, null=True, blank=True)
    
    class Meta:
        verbose_name = _('User Profile')
