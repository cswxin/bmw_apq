#encoding:utf-8

from q_base import QBase
from survey import enums
from survey.q_models import AnswerBlankError, AnswerFormatError
from survey.q_models import regist_q_model
from django.db import connection

class QMultipleScore(QBase):
    u"""
    多项打分题
    [int,int,int]
    """
    _questiontype = enums.QUESTION_TYPE_MULTIPLE_SCORE
    
    def __init__(self, question=None):
        self._question = question
    
    def parse_answer(self, answer):
        if not isinstance(answer, list):
            raise AnswerFormatError()
        new_answer = []
        for item in answer:
            if isinstance(item, (int, long)):
                new_answer.append(item)
            else:
                raise AnswerFormatError()
        return new_answer
    
    def get_column_list(self):
        if not self._question:
            raise Exception('question object not specified!')
        
        column_list = []
        for alt in self._question.alt_list:
            column_list.append(dict(name=('%s__%s' % (self._question.cid, alt.cid)), type='int'))
            if alt.open:
                column_list.append(dict(name=('%s__%s' % (self._question.cid, alt.cid)), type='varchar', length=1000))
        return column_list

    def set_answer(self, respondent_id, answer):
        rid = respondent_id
        answer = self.parse_answer(answer)
        column_list = self.get_column_list()
        name_value_list = []
        for index, column in enumerate(column_list):
            name_value_list.append("%s=%s" % (column['name'], answer[index]))
        name_value_str = ','.join(name_value_list)
        sql = 'update survey_respondentdata set %(name_value_str)s where id = %(rid)s;' % vars()
        
        import DbUtils
        try:
            c, con = DbUtils.cursor()
            c.execute(sql)
            if con:
                con.commit()
        finally:
            if c:
                c.close()
            if con:
                con.close() 
    
    def get_answer(self, respondent_id):
        rid = respondent_id
        column_list = self.get_column_list()
        column_str = ','.join([column['name'] for column in column_list])
        sql = 'select %s from survey_respondentdata where id=%s' % (column_str, respondent_id)
        cursor = connection.cursor()
        cursor.execute(sql)
        result = cursor.fetchone()
        return result
    
    def set_random_answer(self, respondent_id):
        import random
        alt_list = self._question.alt_list
        answer = []
        for alt in alt_list:
            answer.append(random.randint(1, 10))
        self.set_answer(respondent_id, answer)
        
regist_q_model(QMultipleScore)
