#encoding:utf-8
from mc.models import PaperDiff, QuestionDiff
from mc import enums  

def get_all_completed_diffs(term_id, project_id):
    compares = PaperDiff.objects.filter(fw_paper__project__id__in=project_id, fw_paper__term__id=term_id, status__in=[enums.ABSOLUTELY_MATCH, enums.FIXED_CONFLICT])
    return compares                                                 

def get_all_diffs_need_bmw_APQ(term_id, project_id):
    compares = PaperDiff.objects.filter(fw_paper__project__id=project_id, fw_paper__term__id=term_id, status__in=[enums.HAS_CONFLICT, enums.FIXED_CONFLICT])
    return compares   

def get_all_questiondiff_by_diffid(paperdiff_id):
    return QuestionDiff.objects.filter(paper_diff__id=paperdiff_id)
