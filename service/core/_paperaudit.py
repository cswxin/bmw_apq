#encoding:utf-8
from mc.models import PaperAudit
import  constant
def getAuditsByPaperList(paper_list):
    '''paper_list 过大，生成的SQL字符串太长，会导致sqlite 异常，故在此作拆分'''
    size = len(paper_list)
    times = size / constant.maximun
    if  size % constant.maximun > 0:
        times += 1
    audits = []
    for  index in range(0, times):
        start = index * constant.maximun
        end = start + constant.maximun 
        part_ids = paper_list[start: end]
        tmps = PaperAudit.objects.filter(paper__in=part_ids).order_by('paper__id')
        audits.extend(tmps)
        
    return audits
