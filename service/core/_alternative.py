#encoding:utf-8
from survey.models import Alternative
from mcview.decorator import cached
import DbUtils

def get_project_cp_alt_score_dict(project):
    u'''此处获得的选项id,得分字典，有很多是不是检查点，不计分'''
    
    @cached('alt_dict_by_pro_%d' % project.id)
    def __inner():
        u'''仅取有检查点的问题的选项id,得分字字典（检查点中可能还有题目不计分，这里先不管'''
        sql = 'select sa.id, sa.score from survey_checkpoint sc, survey_alternative sa, survey_question sq where sa.question_id = sq.id and sc.question_id = sq.id and sq.project_id=%d and sa.score is not null ' % project.id
        try:
            c, con = DbUtils.cursor()
            c.execute(sql)
            results = c.fetchall()
        finally:
            if c:
                c.close()
            if con:
                con.close() 
        return dict([(data[0], data[1])    for data in results])
            
#        return  dict([(alt.id, alt.score) for alt in Alternative.objects.filter(question_project=project).exclude(score=None)])
    return __inner()
