#encoding:utf-8

"""系统初始化, 在第一次manage.py syncdb之后执行"""

import os, sys
sys.path.insert(0, os.path.abspath(os.curdir))
import settings

from tools.first.user.add_user import add_users
from tools.first.dealer.add_new_term import add_new_term

from init.load_project import add_all_questionnaire
from init.load_checkpoint import update_checkpoint
from init.init_dealer import init_dealer
from service.core._questionqa import init_questionqacolor, init_questionqa
from survey.survey_utils import create_reportdata_table
from tools.excel_to_report import excel2report
from init.update_question_name import update_question_name

def sys_init():
    #期次
    add_new_term()
    #组、权限
    add_users()
    #问卷
    add_all_questionnaire()
    update_checkpoint()
    update_question_name()
    #经销商
    init_dealer()
    #问卷qa
    init_questionqacolor()
    init_questionqa()
    #导入数据大表
#    create_reportdata_table()
#    excel2report(term,'bmw')
#    excel2report(term,'mini')
    
if __name__ == '__main__':
    sys_init()
