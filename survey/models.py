#encoding:utf-8

import os, time, datetime
import cPickle as pickle
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save
from django.db import connection
from django.db.transaction import commit_on_success, set_dirty
from django.contrib.auth.models import User
import enums
import settings

class Project(models.Model):
    name = models.CharField(_('Name'), max_length=50, null=True, blank=True)
    updated = models.DateTimeField(_('Updated'), auto_now=True)
    
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        verbose_name = _('Project')

class Question(models.Model):
    title = models.TextField(_('Title'), max_length=10000, null=True, blank=True)
    project = models.ForeignKey(Project, null=True, blank=True)
    cid = models.CharField(_('Cid'), max_length=50, null=True, blank=True)
    #name_abbr 显示用，后台查询，对比仍用cid
    name_abbr = models.CharField(_('Name Abbr'), max_length=50, null=True, blank=True)
    questiontype = models.IntegerField(_('Questiontype'), choices=enums.CHOICES_QUESTION_TYPE, null=True, blank=True)
    listorder = models.IntegerField(_('Listorder'), null=True, blank=True)
    base_question = models.ForeignKey('self', null=True, blank=True)
    other_type = models.IntegerField(_('Other Type'), null=True, blank=True)
    max_answer_num = models.IntegerField(_('Max Answer Num'), null=True, blank=True)
    updated = models.DateTimeField(_('Updated'), auto_now=True)
    
    def __unicode__(self):
        return u'%s.%s' % (self.name_abbr, self.title)
    
    class Meta:
        verbose_name = _('Question')
    
    @property
    def alt_list(self):
        return Alternative.objects.filter(question=self).order_by('listorder', 'id')
    
    @property
    def has_open_alt(self):
        for alt in self.alt_list:
            if alt.open:
                return True
        return False
#自动更新所属题目的更新时间
def update_project_updated(sender, **kwargs):
    question = kwargs['instance']
    question.project.save()
post_save.connect(update_project_updated, sender=Question)

class QuestionQA(models.Model):
    question = models.ForeignKey(Question, verbose_name=u'原始问题', limit_choices_to={'id__gte':19, })
    q_desc = models.TextField(u'题目说明', max_length=1000, null=True, blank=True)
    a_desc = models.TextField(u'解答或题目详解', max_length=1000, null=True, blank=True)
    q_addon = models.TextField(u'问题', max_length=1000, null=True, blank=True)
    
    q_desc_en = models.TextField(u'题目说明_en', max_length=1000, null=True, blank=True)
    a_desc_en = models.TextField(u'解答或题目详解_en', max_length=1000, null=True, blank=True)
    q_addon_en = models.TextField(u'问题_en', max_length=1000, null=True, blank=True)
    q_en = models.TextField(u'原始问题_en', max_length=1000, null=True, blank=True)
    
    #保存，确保唯一
    def save(self, *arg, **argw):
        if not self.id:
            try:
                qa = QuestionQA.objects.get(question=self.question)
                qa.q_desc = self.q_desc
                qa.a_desc = self.a_desc
                qa.q_addon = self.q_addon
                qa.save()
                return True
            except QuestionQA.DoesNotExist:
                pass
        
        return super(QuestionQA, self).save(*arg, **argw)
    
    class Meta:
        verbose_name = u'问卷常见问题解答'
        verbose_name_plural = u'问卷常见问题解答'

class QuestionAttribute(models.Model):
    question = models.ForeignKey(Question, null=True, blank=True)
    attr_name = models.CharField(_('Attr Name'), max_length=50, null=True, blank=True)
    attr_value = models.CharField(_('Attr Value'), max_length=50, null=True, blank=True)
    
    class Meta:
        verbose_name = _('Question Attribute')

class Alternative(models.Model):
    title = models.TextField(_('Title'), max_length=1000, null=True, blank=True)
    cid = models.CharField(_('Cid'), max_length=50, null=True, blank=True)
    question = models.ForeignKey(Question, null=True, blank=True)
    open = models.BooleanField(_('Open'), default=False)
    listorder = models.IntegerField(_('Listorder'), null=True, blank=True)
    score = models.IntegerField(_('Score'), null=True, blank=True)
    updated = models.DateTimeField(_('Updated'), auto_now=True)
    multiple = models.BooleanField(_('Multiple'), default=False)
    
    def __unicode__(self):
        return self.title
    
    class Meta:
        verbose_name = _('Alternative')
#自动更新所属题目的更新时间
def update_question_updated(sender, **kwargs):
    alt_or_matrixrow = kwargs['instance']
    alt_or_matrixrow.question.save()
post_save.connect(update_question_updated, sender=Alternative)

class AlternativeAttribute(models.Model):
    alternative = models.ForeignKey(Alternative, null=True, blank=True)
    attr_name = models.CharField(_('Attr Name'), max_length=50, null=True, blank=True)
    attr_value = models.CharField(_('Attr Value'), max_length=50, null=True, blank=True)
    
    class Meta:
        verbose_name = _('Alternative Attribute')

class MatrixRow(models.Model):
    title = models.TextField(_('Title'), max_length=1000, null=True, blank=True)
    cid = models.CharField(_('Cid'), max_length=50, null=True, blank=True)
    question = models.ForeignKey(Question, null=True, blank=True)
    listorder = models.IntegerField(_('Listorder'), null=True, blank=True)
    updated = models.DateTimeField(_('Updated'), auto_now=True)
    
    
    def __unicode__(self):
        return self.title
    
    class Meta:
        verbose_name = _('Matrix Row')
post_save.connect(update_question_updated, sender=MatrixRow)

class MatrixRowAttribute(models.Model):
    matrixrow = models.ForeignKey(MatrixRow, null=True, blank=True)
    attr_name = models.CharField(_('Attr Name'), max_length=50, null=True, blank=True)
    attr_value = models.CharField(_('Attr Value'), max_length=50, null=True, blank=True)
    
    class Meta:
        verbose_name = _('Matrix Row Attribute')

class Validator(models.Model):
    name = models.CharField(_('Name'), max_length=50, null=True, blank=True)
    func = models.TextField(_('Func'), max_length=1000, null=True, blank=True)
    error_tip = models.CharField(_('Error Tip'), max_length=50, null=True, blank=True)
    desc = models.CharField(_('Desc'), max_length=50, null=True, blank=True)
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        verbose_name = _('Validator')

class InputValidator(models.Model):
    question = models.ForeignKey(Question, null=True, blank=True)
    alternative = models.ForeignKey(Alternative, null=True, blank=True)
    matrixrow = models.ForeignKey(MatrixRow, null=True, blank=True)
    min = models.IntegerField(_('Min'), null=True, blank=True)
    max = models.IntegerField(_('Max'), null=True, blank=True)
    validator = models.ForeignKey(Validator, null=True, blank=True)
    
    class Meta:
        verbose_name = _('Input Validator')

class Respondent(models.Model):
    status = models.IntegerField(_('Status'), choices=enums.CHOICES_RESPONDENT_STATUS, default=enums.RESPONDENT_STATUS_UNCOMPLETE)
    project = models.ForeignKey(Project, null=True, blank=True)
    user = models.ForeignKey(User, null=True, blank=True)
    start_time = models.DateTimeField(_('Start Time'), auto_now_add=True)
    finish_time = models.DateTimeField(_('Finish Time'), auto_now=True)
        
    class Meta:
        verbose_name = _('Respondent')
    
    def get_data(self, column_name):
        sql = 'select %s from survey_respondentdata where id=%s;' % (column_name, self.id)
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
        if not result:
            return None
        else:
            return result[0]
    
    @property
    def dealer(self):
        from mc.models import Dealer
        dealer_code = self.get_data('dealer_code')
        if dealer_code:
            try:
                return Dealer.objects.get(name=dealer_code)
            except Dealer.DoesNotExist:
                return None
        return None
    
    @property
    def term(self):
        from mc.models import Term
        term_id = self.get_data('term_id')
        if term_id:
            try:
                return Term.objects.get(pk=term_id)
            except Term.DoesNotExist:
                return None
        else:
            return None
    
    @property
    def survey_code(self):
        return self.get_data('survey_code')
    
    @property
    def visit_begin(self):
        visit_date = self.get_data('visit_date')
        visit_begin_time = self.get_data('visit_begin_time')
        datetime_str = '%s %s' % (visit_date, visit_begin_time)
        try:
            return datetime.datetime(*time.strptime(datetime_str, "%Y-%m-%d %H:%M")[0:5])
        except ValueError:
            return None
    
    @property
    def visit_end(self):
        visit_date = self.get_data('visit_date')
        visit_end_time = self.get_data('visit_end_time')
        datetime_str = '%s %s' % (visit_date, visit_end_time)
        try:
            return datetime.datetime(*time.strptime(datetime_str, "%Y-%m-%d %H:%M")[0:5])
        except ValueError:
            return None
    @property
    def visitor_numb(self):
        visitor_numb = self.get_data('visitor_numb')
        if visitor_numb and visitor_numb != '':
            return int(visitor_numb.strip())
        return 0
    @property
    def answers(self):
        import survey_utils
        from q_models import get_q_model
        
        pickle_dir = '%s/project/%s/respondent' % (settings.REL_MEDIA_ROOT, self.project_id)
        pickle_file = '%s/%s.pickle' % (pickle_dir, self.id)
        need_update = False
        if not os.path.exists(pickle_dir):
            os.makedirs(pickle_dir)
            need_update = True
        else:
            if not os.path.exists(pickle_file):
                need_update = True
            else:
                if time.mktime(self.finish_time.timetuple()) >= os.stat(pickle_file)[8]:
                    need_update = True
        
        if need_update:
            answers = {}
            question_list = survey_utils.get_question_list(self.project_id)
            for question in question_list:
                vq = get_q_model(question)
                answers[question.cid] = vq.get_answer(self.id)
            pickle.dump(answers, file(pickle_file, 'wb'))
        else:
            answers = pickle.load(file(pickle_file))
        return answers
    
    def get_translations(self):
        return dict([(translation.column_name, translation.content_en) for translation in Translation.objects.filter(respondent=self)])
     
    def get_translation(self, column_name):
        try:
            rest = Translation.objects.filter(respondent=self, column_name=column_name).order_by('-id')
            return rest[0].content_en
        except IndexError:
            return None
    
    def set_translation(self, column_name, content_en):
        import utils
        translation, is_new = Translation.objects.get_or_create(respondent=self, project=self.project, column_name=column_name)
        translation.content_en = utils.to_unicode(content_en)
        translation.save()
    
    def set_translations(self, adict):
        for column_name, content_en in adict.iteritems():
            self.set_translation(column_name, content_en)
    

#自动添加一条respondentdata记录
def auto_add_respondentdata(sender, **kwargs):
    respondent = kwargs['instance']
    created = kwargs['created']
    import DbUtils
    c, db = DbUtils.cursor()
    if created:
        import DbUtils
        try:
            c, con = DbUtils.cursor()
            c.execute('insert into survey_respondentdata (id) values(%s);' % respondent.id)
            if con:
                con.commit()
        finally:
            if c:
                c.close()
            if con:
                con.close() 
post_save.connect(auto_add_respondentdata, sender=Respondent, dispatch_uid="mcreport.survey.models")

class CheckPoint(models.Model):
    name = models.CharField(_('Name'), max_length=50, null=True, blank=True)
    #name_abbr 显示用，后台查询，对比仍用cid
    name_abbr = models.CharField(_('Name Abbr'), max_length=50, null=True, blank=True)
    desc = models.CharField(_('Desc'), max_length=500, null=True, blank=True)
    desc_en = models.CharField(_('Desc En'), max_length=255, null=True, blank=True)
    question = models.ForeignKey(Question, null=True, blank=True)
    project = models.ForeignKey(Project, null=True, blank=True)
    alternative = models.ForeignKey(Alternative, null=True, blank=True)
    matrixrow = models.ForeignKey(MatrixRow, null=True, blank=True)
    parent = models.ForeignKey('self', null=True, blank=True)
    has_child = models.BooleanField(_('Has Child'), default=False)
    resp_col = models.CharField(_('Resp Col'), max_length=50, null=True, blank=True)
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        verbose_name = _('Check Point')
    
    @property
    def child_list(self):
        return CheckPoint.objects.filter(parent=self).order_by('id')

class Translation(models.Model):
    respondent = models.ForeignKey(Respondent, null=True, blank=True)
    project = models.ForeignKey(Project, null=True, blank=True)
    column_name = models.CharField(_('Column Name'), max_length=50, null=True, blank=True)
    content_en = models.TextField(_('Content Trans'), max_length=1000, null=True, blank=True)
    
    class Meta:
        verbose_name = _('Translation')

class QuestionQAColor(models.Model):
    name = models.TextField(u'部分名称', max_length=100, null=True, blank=True)
    color = models.TextField(u'颜色', max_length=1000, null=True, blank=True)
    
    class Meta:
        verbose_name = u'问卷问与答版块颜色'
        verbose_name_plural = u'问卷问与答版块颜色'

class QuestionQANew(models.Model):
    brand = models.TextField(u'品牌', max_length=100, null=True, blank=True)
    part = models.TextField(u'环节', max_length=100, null=True, blank=True)
    name_cn = models.TextField(u'环节名称_cn', max_length=100, null=True, blank=True)
    name_en = models.TextField(u'环节名称_en', max_length=100, null=True, blank=True)
    number = models.TextField(u'题号', max_length=100, null=True, blank=True)
    question_cn = models.TextField(u'问题_cn', max_length=1000, null=True, blank=True)
    question_en = models.TextField(u'问题_en', max_length=1000, null=True, blank=True)
    option_cn = models.TextField(u'选项_cn', max_length=1000, null=True, blank=True)
    option_en = models.TextField(u'选项_en', max_length=1000, null=True, blank=True)
    point = models.TextField(u'分值', max_length=100, null=True, blank=True)
    desc_cn = models.TextField(u'题目描述_cn', max_length=1000, null=True, blank=True)
    desc_en = models.TextField(u'题目描述_en', max_length=1000, null=True, blank=True)
    color = models.ForeignKey(QuestionQAColor, null=True, blank=True)
    parent = models.ForeignKey('self', null=True, blank=True)
    has_child = models.BooleanField(_('Has Child'), default=False)
    
    class Meta:
        verbose_name = u'问卷问与答'
        verbose_name_plural = u'问卷问与答'

        