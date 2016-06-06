#encoding:utf-8
import os,sys,glob,re
sys.path.insert(0,os.path.abspath(os.curdir))

#from load_permission import add_groups,add_status_perm
from time import sleep
from tools.first.user.add_user import add_users
from tools.first.dealer.add_dealer import add_dealers
from tools.first.dealer.add_new_term import add_new_term

def smk_init():
    #add_groups()
    #add_status_perm()
    print u'初始化期数...',
    add_new_term()
    
    print u'初始化组、权限...',
    add_users()
    print 'ok'
    
#    print u'初始化dealer和user...',
#    add_dealers()
#    print 'ok'
    
    
if __name__ == '__main__':
    smk_init()
