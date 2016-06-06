#encoding:utf-8

from q_base import QBase
from survey import enums
from survey.q_models import AnswerBlankError, AnswerFormatError
from survey.q_models import regist_q_model
from django.db import connection
from survey.models import Alternative

ALT_ID_CID_DICT = {}
def get_alt_cid_by_id(aid):
    cid = ALT_ID_CID_DICT.get(aid)
    if not cid:
        cid = Alternative.objects.get(pk=aid).cid
        ALT_ID_CID_DICT[aid] = cid
    return cid

class QSingle(QBase):
    u"""
    单选题
    无开放式选项  int
    有开放式选项 (int, unicode)
    """
    _questiontype = enums.QUESTION_TYPE_SINGLE
    
    def __init__(self, question=None):
        self._question = question
    
    def parse_answer(self, answer):
        if isinstance(answer, (int, long)):
            return answer
        elif isinstance(answer, list):
            if isinstance(answer[1], unicode):
                return (int(answer[0]), answer[1])
            else:
                return (int(answer[0]), answer[1].decode('utf-8'))
        else:
            raise AnswerFormatError()
    
    def get_column_list(self):
        if not self._question:
            raise Exception('question object not specified!')
        
        column_list = []
        column_list.append(dict(name=self._question.cid, type='int'))
        if self._question.has_open_alt:
            column_list.append(dict(name=('%s__open' % self._question.cid), type='varchar', length=1000))
        return column_list
    
    def set_answer(self, respondent_id, answer):
        rid = respondent_id
        answer = self.parse_answer(answer)
        column_list = self.get_column_list()
        if isinstance(answer, tuple):
            name_value_str = "%s=%s,%s='%s'" % (column_list[0]['name'], answer[0], column_list[1]['name'], answer[1])
        else:
            name_value_str = "%s=%s" % (column_list[0]['name'], answer)
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
        import DbUtils
        try:
            c, con = DbUtils.cursor()
            if len(column_list) == 2:
                sql = 'select %s,%s from survey_respondentdata where id=%s' % (column_list[0]['name'], column_list[1]['name'], respondent_id)
                c.execute(sql)
                aid, alt_open = c.fetchone()
                if not aid:
                    return (None, None)
                cid = get_alt_cid_by_id(aid)
                return (cid, alt_open)
            else:
                sql = 'select %s from survey_respondentdata where id=%s' % (column_list[0]['name'], respondent_id)
                c.execute(sql)
                aid = c.fetchone()[0]
                if not aid:
                    return (None, None)
                cid = get_alt_cid_by_id(aid)
                return (cid, '')
        finally:
                if c:
                    c.close()
                if con:
                    con.close()

    def set_random_answer(self, respondent_id):
        import random
        alt_list = self._question.alt_list
        rand_index = random.randint(0, len(alt_list) - 1)
        alt = alt_list[rand_index]
        if not alt.open:
            self.set_answer(respondent_id, alt.id)
        else:
            self.set_answer(respondent_id, [alt.id, u'用户输入的随机文字. %s' % random.randint(1, 10000)])

regist_q_model(QSingle)
    
