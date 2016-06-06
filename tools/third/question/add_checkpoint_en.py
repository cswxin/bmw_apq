#encoding:utf-8

import os, sys
sys.path.insert(0, os.path.abspath(os.curdir))

from survey.models import CheckPoint

from django.db.transaction import commit_on_success, commit_manually, commit, set_dirty
import xlrd
import string
from django.conf import settings

@commit_on_success
def add_checkpoint_en(sheet, project_id):
    for rx in range(0, sheet.nrows):
        texts = sheet.row_values(rx)
        cp_name_abbr = texts[0].strip()
        cp_desc_en = texts[1].strip()
        print cp_name_abbr, project_id
        cp = CheckPoint.objects.get(name_abbr=cp_name_abbr, project__id=project_id)
        cp.desc_en = cp_desc_en
        cp.save()
    set_dirty()

def add_BMW_EN():
    xlsfile = os.path.join(settings.RESOURCES_ROOT, u'first/checkpoint/BMW_EN.xls')
    book = xlrd.open_workbook(xlsfile)
    sh = book.sheet_by_index(0)
    print sh.name, sh.nrows, sh.ncols
    add_checkpoint_en(sh, 2)
    
def add_MINI_EN():
    xlsfile = os.path.join(settings.RESOURCES_ROOT, u'first/checkpoint/MINI_EN.xls')
    book = xlrd.open_workbook(xlsfile)
    sh = book.sheet_by_index(0)
    print sh.name, sh.nrows, sh.ncols
    add_checkpoint_en(sh, 3)

def add_Competitors_EN():
    xlsfile = os.path.join(settings.RESOURCES_ROOT, u'first/checkpoint/competitors_EN.xls')
    book = xlrd.open_workbook(xlsfile)
    sh = book.sheet_by_index(0)
    print sh.name, sh.nrows, sh.ncols
    add_checkpoint_en(sh, 4)
    
@commit_on_success
def add_EN():
    add_BMW_EN()
    add_MINI_EN()
    add_Competitors_EN()
    
if __name__ == '__main__':
    add_EN()
