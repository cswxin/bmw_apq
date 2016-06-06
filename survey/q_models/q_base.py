#encoding:utf-8
from mc.models import *

class QBase(object):

    _questiontype = None
    
    def __init__(self,question=None):
        pass
    
    def set_question(question):
        self._question = question
    
    def parse_answer(self, answer):
        """
        验证答案格式是否正确
        """
        raise NotImplementedError(self.__class__.__name__ + '.parse_answer')

