#encoding:utf-8
from userpro.models import UserProfile
from userpro import enums
from mc.enums import STATUS_PERM_DICT
from django.contrib.auth.models import User

#判断是否有管理员权限
def has_manage_perm(user):
    return check_user_perm(user, enums.MANAGER_PERMISSION)

#翻译权限
def has_tran_perm(user):
    return check_user_perm(user, enums.TRAN_PERMISSION)

#录入权限(FW,FH)
def has_input_perm(user):
    return has_fw_input_perm(user) or has_fh_input_perm(user)

def has_fw_input_perm(user):
    return check_user_perm(user, enums.FW_INPUT_PERMISSION)

def has_fh_input_perm(user):
    return check_user_perm(user, enums.FH_INPUT_PERMISSION)

#QC1审核权限
def has_qc1_audit_perm(user):
    return check_user_perm(user, enums.FW_BEGIN_AUDIT_PERMISSION)

#QC2 审核权限
def has_qc2_audit_perm(user):
    return check_user_perm(user, enums.FW_QC_AUDIT_PERMISSION)

#QC3审核权限
def has_qc3_audit_perm(user):
    return check_user_perm(user, enums.FW_QC_AUDIT_PERMISSION2)

#督导审核权限
def has_dd_audit_perm(user):
    return check_user_perm(user, enums.FW_AREA_AUDIT_PERMISSION)

#研究审核
def has_yj_audit_perm(user):
    return check_user_perm(user, enums.FW_AUDIT_PERMISSION)

#GFK终审审核权限
def has_end_audit_perm(user):
    return check_user_perm(user, enums.FW_END_AUDIT_PERMISSION)

#FH审核
def has_fh_audit_perm(user):
    return check_user_perm(user, enums.FH_AUDIT_PERMISSION)

#FH终审审核权限
def has_fh_end_audit_perm(user):
    return check_user_perm(user, enums.FH_END_AUDIT_PERMISSION)

#查看所有页面权限
def has_all_page_perm(user):
    return check_user_perm(user, enums.SHOW_ALL_PAGE)

#查看非执行进度页面权限
def has_run_page_perm(user):
    return check_user_perm(user, enums.SHOW_NO_RUN_PAGE)

#经销商页面权限
def has_dealer_page_perm(user):
    return check_user_perm(user, enums.SHOW_DEALER_PAGE)

#获得负责的经销商
def get_dealer_by_user(user):
    up, create = UserProfile.objects.get_or_create(user=user)
    return up.dealer

##用户是否为GFK组
#def check_user_in_gfk_group(user):
#    return check_user_group(user, [enums.FW_INPUT_GROUP, enums.FW_AUDIT_GROUP, enums.FW_DUDAO_GROUP])

##用户是否为复核组
#def check_user_in_fh_group(user):
#    return check_user_group(user, [enums.FH_INPUT_GROUP, enums.FH_AUDIT_GROUP])

#用户是否为经销商组
def check_user_in_dealer_group(user):
    return check_user_group(user, [enums.DEALER_GROUP])

def check_user_group(user, group_names):
    dbuser = User.objects.filter(id=user.id, groups__name__in=group_names)
    flag = False
    if dbuser and len(dbuser) > 0:
        flag = True
    return flag

def check_user_perm(user, perm):
    perms = get_user_perms(user)
    return perm in perms

def has_perm_define(user, *perms):
    ownered = get_user_perms(user)
    has = False
    for p in perms:
        if p in ownered:
            has = True
    return has
def is_only_input(user):
    if has_perm_define(user, enums.MANAGER_PERMISSION,
                       enums.FW_BEGIN_AUDIT_PERMISSION,
                       enums.FW_QC_AUDIT_PERMISSION,
                       enums.FW_QC_AUDIT_PERMISSION2,
                       enums.FW_AREA_AUDIT_PERMISSION,
                       enums.FW_AUDIT_PERMISSION,
                       enums.FW_END_AUDIT_PERMISSION,
                       ):
        return False
    elif has_input_perm(user):
        return True
    return False

def get_user_max_perm(user):
    perms = get_user_perms(user)
    max_perm = 0
    for ps in perms:
        perm = STATUS_PERM_DICT.get(ps, 0)
        if perm > max_perm:
            max_perm = perm
    return max_perm

def get_user_perms(user):
    from mcview.decorator import cached
    @cached('user_key_%s' % (user.username))
    def _inner(user, attrs):
        up, create = UserProfile.objects.get_or_create(user=user)
        user.perms = [u.name for u in up.user_permissions.all()]
        return user
    return _inner(user, attrs='perms').perms

#def getUsers():
#    from mcview.decorator import cached
#    @cached('qcusers')
#    def _inner():
#        #得到访问员
#        ups = UserProfile.objects.filter(user_permissions__name=enums.FW_INPUT_PERMISSION, user__groups__name=enums.FW_INPUT_GROUP)
#        ret = [u.user for u in ups if u.user.is_active]
#        return set(ret)
#    return _inner()
