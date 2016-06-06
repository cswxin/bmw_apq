#encoding:utf-8

import os, sys
sys.path.insert(0, os.path.abspath(os.curdir))
import settings
from survey.models import CheckPoint

def update_question_name():
    sub_cp_list = CheckPoint.objects.filter(has_child=False)
    for sub_cp in sub_cp_list:
        if not sub_cp.desc_en:
            desc_list = sub_cp.desc.split('<br>')
            sub_cp.desc = desc_list[0]
            sub_cp.desc_en = desc_list[1]
            sub_cp.save()
            
    cp_name_dict = {'A':'Appointment scheduling',
     'B':'Vehicle Drop-off & Checking',
     'C':'Vehicle Pick-up',
     'D':'Billing',
     'E':'Farewell',
     'F':'Overall Assessmen',
     'G':'Chinese Specific Questions'}
    
    for name,desc_en in cp_name_dict.items():
        cp_list = CheckPoint.objects.filter(name=name)
        for cp in cp_list:
            cp.desc_en = desc_en
            cp.save()
            
if __name__ == '__main__':
    update_question_name()