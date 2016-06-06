#encoding:utf-8

from django.db.transaction import commit_on_success
from django.contrib.auth.models import User,Group,Permission
from userpro.models import UserPermission
import sys,os

mc_groups = (
(u'经销商',{}),
(u'访问员',{u'问卷':'add',}),
(u'QC审核',{u'问卷':'change',}),
(u'独立复核',{u'问卷':'change,add',}),
(u'系统管理员',{u'问卷':'all',u'报告':'all','user':'all','group':'all',u'期次':'all',})
)

from userpro.enums import MC_PERMISSIONS

@commit_on_success
def add_groups():
    #Group.objects.all().delete()
    
    for gname,perdict in mc_groups:
        g,create = Group.objects.get_or_create(name=gname)
        ps = []
        for key,perm in perdict.items():
            perms = []
            if perm == 'all':
                perms.append(u'Can add %s' % key)
                perms.append(u'Can delete %s' % key)
                perms.append(u'Can change %s' % key)
            else:
                pnames = perm.split(',')
                for pname in pnames:
                    perms.append(u'Can %s %s' % (pname,key))
            
            for pm in perms:
                p = Permission.objects.get(name=pm)
                ps.append(p)
        
        g.permissions = ps
        g.save()
    
@commit_on_success
def add_permissions():
    for pname in MC_PERMISSIONS:
        p,create = UserPermission.objects.get_or_create(name=pname)
    
if __name__ == '__main__':
    add_permissions()
    add_groups()
    