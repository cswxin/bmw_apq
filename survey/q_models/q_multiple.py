#encoding:utf-8

from q_base import QBase
from survey import enums
from survey.q_models import AnswerBlankError, AnswerFormatError
from survey.q_models import regist_q_model
from django.db import connection

class QMultiple(QBase):
    u"""
    多选题
    [int,int,(int,unicode),int]
    """
    _questiontype = enums.QUESTION_TYPE_MULTIPLE
    
    def __init__(self, question=None):
        self._question = question
    
    def parse_answer(self, answer):
        if not isinstance(answer, list):
            raise AnswerFormatError()
        new_answer = []
        for item in answer:
            if isinstance(item, (int, long)):
                new_answer.append(item)
            elif isinstance(item, list):
                new_answer.append((int(item[0]), item[1].decode('utf-8')))
            else:
                raise AnswerFormatError()
        return new_answer
    
    def get_column_list(self):
        if not self._question:
            raise Exception('question object not specified!')
        
        column_list = []
        for alt in self._question.alt_list:
            column_list.append(dict(name=('%s__%s' % (self._question.cid, alt.cid)), type='bool'))
            if alt.open:
                column_list.append(dict(name=('%s__%s__open' % (self._question.cid, alt.cid)), type='varchar', length=1000))
        return column_list
    
    def set_answer(self, respondent_id, answer):
        rid = respondent_id
        answer = self.parse_answer(answer)
        column_list = self.get_column_list()
        raise Exception('not implemented yet')
    
    def get_answer(self, respondent_id):
        rid = respondent_id
        column_list = self.get_column_list()
        raise Exception('not implemented yet')
regist_q_model(QMultiple)
