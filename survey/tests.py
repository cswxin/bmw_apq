#encoding:utf-8

"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
import settings
from django.db import connection


class SimpleTest(TestCase):
    
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.failUnlessEqual(1 + 1, 2)

class QModelTest(TestCase):
    fixtures = ['survey.json']
    
    def test_create_respodentdata_table(self):
        import DbUtils
        c, db = DbUtils.cursor()
        c.execute('drop table if exists survey_respondentdata;')
        from survey.survey_utils import create_respodentdata_table
        create_respodentdata_table(1)
    
    def test_q_models(self):
        from survey.models import *
        from survey import q_models        
        r = Respondent()
        r.save()
        
        q = Question.objects.get(pk=10) #单选题
        q_model = q_models.get_q_model(q)
        q_model.set_answer(r.id, 1000)
        q_model.get_answer(r.id)
        q_model.set_answer(r.id, [1000, u'asdfasdf'])
        q_model.get_answer(r.id)
        
        q = Question.objects.get(pk=1) #填空题
        q_model = q_models.get_q_model(q)
        q_model.set_answer(r.id, '张三')
        print q_model.get_answer(r.id)
                
        q = Question.objects.get(pk=60) #多项填空题
        q_model = q_models.get_q_model(q)
        q_model.set_answer(r.id, ['张三1', '张三2', '张三3', '张三4'])
        print q_model.get_answer(r.id)
        
        q = Question.objects.get(pk=65) #多项打分题
        q_model = q_models.get_q_model(q)
        q_model.set_answer(r.id, [5])
        print q_model.get_answer(r.id)
        


