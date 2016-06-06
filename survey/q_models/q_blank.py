#encoding:utf-8

from q_base import QBase
from survey import enums
from survey.q_models import AnswerBlankError, AnswerFormatError
from survey.q_models import regist_q_model
from django.db import connection

class QBlank(QBase):
    u"""
    填空题
    unicode
    """
    _questiontype = enums.QUESTION_TYPE_BLANK
    
    def __init__(self, question=None):
        self._question = question
    
    def parse_answer(self, answer):
        if isinstance(answer, unicode):
            return answer
        elif isinstance(answer, str):
            return answer.decode('utf-8')
        else:
            raise AnswerFormatError()
    
    def get_column_list(self):
        if not self._question:
            raise Exception('question object not specified!')
        
        column_list = []
        column_list.append(dict(name=self._question.cid, type='varchar', length=1000))
        return column_list

    def set_answer(self, respondent_id, answer):
        rid = respondent_id
        answer = self.parse_answer(answer)
        column_list = self.get_column_list()
        name_value_str = "%s='%s'" % (column_list[0]['name'], answer)
        sql = 'update survey_respondentdata set %(name_value_str)s where id = %(rid)s;' % vars()
        import DbUtils
        try:
            c, con = DbUtils.cursor()
            c.execute(sql)
            if con:
                con.commit();
        finally:
            if c:
                c.close()
            if con:
                con.close() 
    
    def get_answer(self, respondent_id):
        rid = respondent_id
        column_list = self.get_column_list()
        sql = 'select %s from survey_respondentdata where id=%s' % (column_list[0]['name'], respondent_id)
        import DbUtils
        try:
            c, con = DbUtils.cursor()
            c.execute(sql)
            result = c.fetchone()
        finally:
            if c:
                c.close()
            if con:
                con.close() 
        return result[0]
    
    def set_random_answer(self, respondent_id):
        import random
        self.set_answer(respondent_id, u'用户输入的随机文字. %s' % random.randint(1, 10000))

regist_q_model(QBlank)
    
