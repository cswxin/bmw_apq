#encoding:utf-8

class AnswerBlankError(Exception):
    """The answer is blank. A json string is required."""

class AnswerFormatError(Exception):
    """Answer format error."""

Q_MODEL_DICT = {}
def regist_q_model(q_model):
    Q_MODEL_DICT[q_model._questiontype] = q_model

def get_q_model(question):
    q_model = Q_MODEL_DICT.get(question.questiontype)
    return q_model(question)

import q_single,q_multiple,q_blank,q_multiple_blank,q_multiple_score