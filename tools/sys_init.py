#encoding:utf-8

"""系统初始化, 在第一次manage.py syncdb之后执行"""
import os,sys
sys.path.insert(0,os.path.abspath(os.curdir))

from tools.question import add_question,add_project,add_question_qa
from tools.dealer import add_dealer,add_term,update_dealer_name
from tools.checkpoint import add_checkpoint
from tools.user import add_permission,add_user
from survey.survey_utils import create_respodentdata_table,create_reportdata_table
from tools.city import add_city
import settings

def sys_init():
    if not os.path.exists('%s/static/mcview/images/chart' % settings.SITE_ROOT):
        os.makedirs('%s/static/mcview/images/chart' % settings.SITE_ROOT)
    
    print u'初始化权限数据 ...',
    add_permission.add_permissions()
    add_permission.add_groups()
    print 'OK!'
    
    print u'初始化省份城市 ...',
    add_city()
    print 'OK!'
    
    print u'初始化Survey相关数据 ...',
    add_project()
    add_question()
    add_question_qa()
    print 'OK!'
    
    print u'初始化经销商类型 ...',
    add_dealer.clean_table()
    add_dealer.add_dealertype()
    print 'OK!'
    
    print u'初始化宝马经销商 ...',
    add_dealer.add_bmw_dealer()
    print 'OK!'
    
    print u'初始化竞品经销商 ...',
    add_dealer.add_other_dealer()
    print 'OK!'
    
    print u'更新经销商名称 ...',
    update_dealer_name.update_dealer_name()
    print 'OK!'
    
    print u'对经销商表进行排序 ...',
    add_dealer.update_dealer_listorder()
    print 'OK!'
    
    print u'初始化期数表 ...',
    add_term.add_term()
    print 'OK!'
    
    print u'初始化检查点 ...',
    add_checkpoint.update_checkpoint()
    print 'OK!'
    create_respodentdata_table(1)
    create_reportdata_table(1)
    
    print u'初始化用户帐号 ...',
    add_user.add_users()
    print 'OK!' 
    
    pass

if __name__ == '__main__':
    sys_init()