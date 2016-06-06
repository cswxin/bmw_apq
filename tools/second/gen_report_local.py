#encoding:utf-8
import os, sys, shutil
sys.path.insert(0, os.path.abspath(os.curdir))
from mc.models import Question, PaperDiff
from service.core._question import restore_result
import DbUtils
import xlrd
from service.core import _report, _paper, _term
from mc.models import XslReport, Paper
from survey.models import CheckPoint, Alternative, Translation
from django.conf import settings
from survey import survey_utils
from mc import enums
import logging  
logging.basicConfig(filename=os.path.join(os.getcwd(), 'log.txt'), level=logging.WARN, filemode='w', format='%(asctime)s - %(levelname)s: %(message)s') 


def gen_excel_report(term):
    
    # BMW
    papers = Paper.objects.filter(term = term, paper_type='BMW', project__id=2)
    for p in papers:
        print 'gen ',p.dealer.name_cn, 'paperid=', p.id
        from mc import gen_report
        gen_report(p, None)
        print 'finish ', p.dealer.name_cn
    #MINI 
    papers = Paper.objects.filter(term = term, paper_type='BMW', project__id=3)
    for p in papers:
        print 'gen ',p.dealer.name_cn, 'paperid=', p.id
        from mc import gen_report
        gen_report(p, None)
        print 'finish ', p.dealer.name_cn

    
#    plist = ['30933','35314','27365','28402','35007']
#    plist = ['33150','32354','33876','27357','35617']
#    for pname in plist:
#        p = Paper.objects.get(term=term, paper_type='BMW',project__id=2, dealer__name=pname)
#        print 'gen ',p.dealer.name_cn, 'paperid=', p.id
#        from mc import gen_report
#        gen_report(p, None)
#        print 'finish ', p.dealer.name_cn
    
    
        

        
if __name__ == '__main__':
    term = _term.get_cur_input_term()
    print term.name_cn
    gen_excel_report(term)