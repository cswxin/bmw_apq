#encoding:utf-8

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import pre_delete, post_delete
from django.contrib.auth.models import User
from django.db import connection
from survey.models import Respondent, Project, Question
import enums
from datetime import datetime
from django.db.transaction import commit_on_success, set_dirty

replaceuploadchar = ['%20', ' ', '(', ')', '!']

class Province(models.Model):
    name = models.CharField(_('Name'), max_length=50, null=True, blank=True)
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        verbose_name = _('Province')

class City(models.Model):
    name = models.CharField(_('Name'), max_length=50, null=True, blank=True)
    province = models.ForeignKey(Province, null=True, blank=True)
    sn = models.IntegerField(_('Sn'), default=0)
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        verbose_name = _('City')

class DealerType(models.Model):
    name_cn = models.CharField(_('Name Cn'), max_length=50, null=True, blank=True)
    name_en = models.CharField(_('Name En'), max_length=50, null=True, blank=True)
    
    def __unicode__(self):
        return self.name_cn
    
    class Meta:
        verbose_name = _('Dealer Type')

class Dealer(models.Model):
    name = models.CharField(u'公司代码', max_length=50, null=True, blank=True)
    dealertype = models.ForeignKey(DealerType, verbose_name=u'类型', null=True, blank=True)
    name_cn = models.CharField(u'公司名称', max_length=255, null=True, blank=True)
    name_en = models.CharField(u'英文名称', max_length=255, null=True, blank=True)
    abbr_cn = models.CharField(u'简称', max_length=255, null=True, blank=True)
    abbr_en = models.CharField(u'英文简称', max_length=255, null=True, blank=True)
    city_cn = models.CharField(u'城市', max_length=50, null=True, blank=True)
    city_en = models.CharField(u'城市英文名', max_length=50, null=True, blank=True)
    province_cn = models.CharField(u'省份', max_length=50, null=True, blank=True)
    province_en = models.CharField(u'省份英文名', max_length=50, null=True, blank=True)
    address = models.CharField(u'地址', max_length=200, null=True, blank=True)
    tel = models.CharField(u'电话', max_length=200, null=True, blank=True)
    email = models.CharField(u'邮箱', max_length=200, null=True, blank=True)
    parent = models.ForeignKey('self', verbose_name=u'区域', null=True, blank=True, limit_choices_to={'has_child': True})
    jt_parent = models.ForeignKey('self', null=True, blank=True, related_name='mymodel1_dealer')
    xq_parent = models.ForeignKey('self', null=True, blank=True, related_name='mymodel2_dealer')
    sf_parent = models.ForeignKey('self', null=True, blank=True, related_name='mymodel3_dealer')
    dt_parent = models.ForeignKey('self', null=True, blank=True, related_name='mymodel4_dealer')
    termid = models.IntegerField(_('Term Id'), null=True, blank=True)
    has_child = models.BooleanField(_('Has Child'), default=True)
    listorder = models.IntegerField(_('Listorder'), null=True, blank=True)
    level = models.IntegerField(_('Level'), null=True, blank=True)    
    new_old = models.CharField(u'新店老店', max_length=255, null=True, blank=True)
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        verbose_name = u'经销商'
        verbose_name_plural = u'经销商'
    
    @property
    def region(self):
        obj = self
        while obj.parent.parent:
            obj = obj.parent
        return obj
    
    @property
    def city(self):
        return self.parent
    
    @property
    def nation(self):
        #return Dealer.objects.get(parent=None)
        return Dealer.objects.filter(parent=None).order_by('id')[0]

class Term(models.Model):
    name = models.CharField(u'名称', max_length=50)
    name_cn = models.CharField(_('Name Cn'), max_length=50, null=True, blank=True)
    name_en = models.CharField(_('Name En'), max_length=50, null=True, blank=True)
    begin = models.DateTimeField(u'开始时间', null=True, blank=True)
    is_active = models.BooleanField(u'当前显示期数', default=False)
    is_active_input = models.BooleanField(u'当前录入期数', default=False)
    end = models.DateTimeField(u'结束时间', null=True, blank=True)
    listorder = models.IntegerField(_('Listorder'), default=0)
    testonly = models.BooleanField(u'测试期间，不对经销商开放', default=False)
    dealers = models.ManyToManyField(Dealer, verbose_name=u'本期的经销商', null=True, blank=True)
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        verbose_name = u'Term'
        verbose_name_plural = u'Term'
    
    def is_finished(self):
#        now = datetime.now()
#        if self.end and self.end < now:
#            return True
#        return False
        return True

class DealerPosition(models.Model):
    dealer = models.ForeignKey(Dealer, null=True, blank=True)
    term = models.ForeignKey(Term, null=True, blank=True)
    position_region = models.IntegerField(_('Position Region'), null=True, blank=True)
    count_region = models.IntegerField(_('Count Region'), null=True, blank=True)
    position_nation = models.IntegerField(_('Position Nation'), null=True, blank=True)
    count_nation = models.IntegerField(_('Count Nation'), null=True, blank=True)
    Total = models.FloatField(_('Total'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('Dealer Position')

class Report(models.Model):
    respondent = models.ForeignKey(Respondent, null=True, blank=True)
    paper_type = models.CharField(u'团队', choices=enums.CHOICES_PAPER_TYPE, max_length=50, editable=False, null=True, blank=True)
    project = models.ForeignKey(Project, editable=False, null=True, blank=True)
    dealer = models.ForeignKey(Dealer, null=True, blank=True)
    dealer_name = models.CharField(_('Dealer Name'), max_length=255, null=True, blank=True)
    dealertype = models.ForeignKey(DealerType, null=True, blank=True)
    term = models.ForeignKey(Term, null=True, blank=True)
    term_name = models.CharField(_('Term Name'), max_length=50, null=True, blank=True)
    score = models.FloatField(_('Score'), null=True, blank=True)
    part_a = models.FloatField(_('PartA'), null=True, blank=True)
    part_b = models.FloatField(_('PartB'), null=True, blank=True)
    is_public = models.BooleanField(_('Is Public'), default=False)
    score_str = models.TextField(max_length=5000, null=True, blank=True, editable=False)
    answer_str = models.TextField(max_length=5000, null=True, blank=True, editable=False)
    
    
    def __unicode__(self):
        str = u'%s' % (self.dealer.name)
        if self.term:
            str += u' %s' % self.term.name
        
        return str
    
    class Meta:
        verbose_name = _('Report')

class DealerVisitor(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    dealer = models.ForeignKey(Dealer, null=True, blank=True)
    term = models.ForeignKey(Term, null=True, blank=True)
    plan_begin = models.DateTimeField(_('Plan Begin'), null=True, blank=True)
    plan_end = models.DateTimeField(_('Plan End'), null=True, blank=True)
    respondent = models.ForeignKey(Respondent, null=True, blank=True)
    status = models.IntegerField(_('Status'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('Dealer Visitor')

class DealerManager(models.Model):
    dealer = models.ForeignKey(Dealer, null=True, blank=True)
    user = models.ForeignKey(User, null=True, blank=True)
    
    class Meta:
        verbose_name = _('Dealer Manager')

def upload_document_path(inst, filename):
    for c in replaceuploadchar:
        filename = filename.replace(c, '_')
    
    nowday = datetime.today()
    return u'document/%d/%d/%d/%s' % (nowday.year, nowday.month, nowday.day, filename)

class ReportDocument(models.Model):
    title = models.CharField(u'标题', max_length=200, null=True, blank=True)
    term = models.ForeignKey(Term, verbose_name=u'期数', null=True, blank=True)
    document = models.FileField(verbose_name=u'文档', upload_to=upload_document_path, null=True, blank=True)
    areacode = models.IntegerField(_('Areacode'), default=1, choices=enums.CHOICES_AREA_TYPE)
    
    class Meta:
        verbose_name = u'Report'
        verbose_name_plural = u'Report'
    
class Paper(models.Model):
    user = models.ForeignKey(User, editable=False)
    paper_type = models.CharField(u'团队', default=enums.FW_PAPER_TYPE, choices=enums.CHOICES_PAPER_TYPE, max_length=50, editable=False, null=True, blank=True)
    survey_code = models.CharField(_('Survey Code'), max_length=50, null=True, blank=True, editable=False)
    respondent = models.ForeignKey(Respondent, editable=False, null=True, blank=True)
    dealer = models.ForeignKey(Dealer, editable=False, null=True, blank=True)
    term = models.ForeignKey(Term, editable=False, null=True, blank=True)
    project = models.ForeignKey(Project, editable=False, null=True, blank=True)
    visit_begin = models.DateTimeField(_('Visit Begin'), null=True, blank=True)
    visit_end = models.DateTimeField(_('Visite End'), null=True, blank=True)
    visitor_num = models.IntegerField(u'进店人数', default=0, null=True, blank=True)
    status = models.IntegerField(_('Status'), default=0, choices=enums.CHOICES_PAPER_STATUS, editable=False)
    score = models.FloatField(_('Score'), null=True, blank=True)
    is_public = models.BooleanField('发布', default=False)
    
    def __unicode__(self):
        name = u''
        if self.dealer:
            name = u'%s ' % self.dealer.name
        if self.survey_code:
            name += self.survey_code
        if self.term:
            name += u' %s' % self.term.name
        
        return name
    
    class Meta:
        #unique_together = ('dealer', 'term')
        verbose_name = u'问卷'
        verbose_name_plural = u'问卷列表'
    
    @property
    def report_ready(self):
        return self.status >= enums.PAPER_STATUS_FINISH
        #return self.status >= enums.PAPER_STATUS_FINISH and XslReport.objects.filter(paper=self).count() > 0
@commit_on_success
def delete_paper_related_respondent(sender, **kwargs):
    paper = kwargs['instance']
    
    try:
        if paper.respondent is None:
            return
    except Respondent.DoesNotExist, e:
        return 
    #1. 删除 report_data, report
    try:
        reports = Report.objects.filter(respondent=paper.respondent)
        if reports and len(reports) > 0:
            report_ids = [str(rep.id) for rep in reports]
            
            report_id_str = ','.join(report_ids)
            from DbUtils import cursor
            try:
                c, con = cursor()
                if report_ids and len(report_ids) > 0:
                    sql_r = "delete from mc_report where id in( %s)" % report_id_str
                    c.execute(sql_r)
                    sql = 'delete from mc_reportdata where id in (%s)' % report_id_str
                    c.execute(sql)
                    if con:
                        con.commit()
            finally:
                if c:
                    c.close()
                if con:
                    con.close() 
    except:
        pass
    
    #2. 删除respondent_data, respondent
    resp_id = paper.respondent.id
    try:
        Respondent.objects.get(pk=resp_id).delete()
        from DbUtils import cursor
        try:
            c, con = cursor()
            sql = 'delete from survey_respondentdata where id =%d' % resp_id
            c.execute(sql)
            if con:
                con.commit()
        finally:
            if c:
                c.close()
            if con:
                con.close() 
    except:
        pass
    #3. 删除translation
#    try:
#        from DbUtils import cursor
#        c, con = cursor()
#        sql = 'delete from survey_translation where respondent_id =%d' % resp_id
#        c.execute(sql)
#        if con:
#            con.commit()
#    finally:
#        if c:
#            c.close()
#        if con:
#            con.close() 
    #4. 删除questiondiff, paperdiff
#    try:
#        from DbUtils import cursor
#        c, con = cursor()
#        key = 'fw_paper_id'
#        if paper.paper_type == enums.FW_PAPER_TYPE:
#            key = 'fw_paper_id'
#        elif paper.paper_type == enums.FH_PAPER_TYPE:
#            key = 'fh_paper_id'
#        elif paper.paper_type == enums.BMW_PAPER_TYPE:
#            key = 'final_paper_id'
#        
#        questionsql = 'delete from mc_questiondiff where paper_diff_id in ( select id from mc_paperdiff where %s =%d)' % (key, resp_id)
#        c.execute(questionsql)
#        if con:
#            con.commit()
#        
#        papersql = 'delete from mc_paperdiff where %s =%d' % (key, resp_id)
#        c.execute(papersql)
#        if con:
#            con.commit()
#    finally:
#        if c:
#            c.close()
#        if con:
#            con.close() 
    return
post_delete.connect(delete_paper_related_respondent, sender=Paper)

def upload_image_path(inst, filename):
    for c in replaceuploadchar:
        filename = filename.replace(c, '_')
    
    import random
    ranid = random.randint(1, 9999)
    nowday = datetime.today()
    return u'image/%d/%d/%d/%d_%s' % (nowday.year, nowday.month, nowday.day, ranid, filename)

def upload_sound_path(inst, filename):
    for c in replaceuploadchar:
        filename = filename.replace(c, '_')
    import random
    ranid = random.randint(1, 9999)
    nowday = datetime.today()
    return u'sound/%d/%d/%d/%d_%s' % (nowday.year, nowday.month, nowday.day, ranid, filename)
    
class ReportSound(models.Model):
    user = models.ForeignKey(User)
    paper = models.ForeignKey(Paper)
    sound = models.FileField(verbose_name=u'声音', upload_to=upload_sound_path)
    created = models.DateTimeField(verbose_name=u'上传时间', auto_now_add=True)
    last_modify = models.DateTimeField(verbose_name=_('last_modify'), auto_now=True)
    
    class Meta:
        verbose_name = u'录音文件'
        verbose_name_plural = u'录音文件'

class ReportImage(models.Model):
    user = models.ForeignKey(User)
    paper = models.ForeignKey(Paper)
    image = models.ImageField(verbose_name=u'图片', upload_to=upload_image_path)
    #image = models.CharField(verbose_name=u'线路', max_length=200)
    created = models.DateTimeField(verbose_name=u'上传时间', auto_now_add=True)
    last_modify = models.DateTimeField(verbose_name=_('last_modify'), auto_now=True)
    
    class Meta:
        verbose_name = u'图片文件'
        verbose_name_plural = u'图片文件'

def upload_xsl_path(inst, filename):
    for c in replaceuploadchar:
        filename = filename.replace(c, '_')
    
    nowday = datetime.today()
    return u'xsl/%d/%d/%d/%s' % (nowday.year, nowday.month, nowday.day, filename)

class XslReport(models.Model):
    paper = models.ForeignKey(Paper, null=True, blank=True)
    xslfile = models.FileField(_('Xslfile'), upload_to=upload_xsl_path, null=True, blank=True)
    
    class Meta:
        verbose_name = _('Xsl Report')

class XlsReportHist(models.Model):
    dealer = models.ForeignKey(Dealer, null=True, blank=True)
    term_index = models.IntegerField(_('Term Index'), null=True, blank=True)
    xlsfile = models.FileField(_('Xlsfile'), upload_to=upload_xsl_path, null=True, blank=True)
    score = models.FloatField(_('Score'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('Xls Report Hist')

class PaperAudit(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    paper = models.ForeignKey(Paper, null=True, blank=True)
    created = models.DateTimeField(_('Created'), auto_now_add=True)
    old_status = models.IntegerField(_('Old Status'), null=True, blank=True, default=0, choices=enums.CHOICES_PAPER_STATUS)
    new_status = models.IntegerField(_('New Status'), null=True, blank=True, default=0, choices=enums.CHOICES_PAPER_STATUS)
    
    class Meta:
        verbose_name = _('Paper Audit')

class PaperAuditItem(models.Model):
    paperaudit = models.ForeignKey(PaperAudit, null=True, blank=True)
    question_id = models.IntegerField(_('Question Id'), null=True, blank=True)
    old_answer = models.TextField(_('Old Answer'), max_length=10000, null=True, blank=True)
    new_answer = models.TextField(_('New Answer'), max_length=10000, null=True, blank=True)
    valid = models.BooleanField(_('Valid'), default=False)
    created = models.DateTimeField(_('Created'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Paper Audit Item')

class Router(models.Model):
    name = models.CharField(_('Name'), max_length=50)
    term = models.ForeignKey(Term)
    citys = models.CharField(verbose_name=u'线路', max_length=500)
    user = models.ForeignKey (User, null=True, blank=True)
    updated = models.DateTimeField(_('Updated'), auto_now=True)
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        verbose_name = u'线路分配表'
        verbose_name_plural = u'线路分配表'


'''差异问卷的id对
    status字段标记 问卷是否有差异，若比对的问卷不存在差异，也会插一条，以记录比对的两个paper
    在删除问卷时一并删除paperdiff记录
'''        
class PaperDiff(models.Model):
    fw_paper = models.ForeignKey(Paper, related_name='p1')
    fh_paper = models.ForeignKey(Paper, related_name='p2')
    final_paper = models.ForeignKey(Paper, related_name='final', null=True, blank=True)
    status = models.IntegerField(_('Status'), default=0, choices=enums.CHOICES_DIFF_STATUS, editable=False)
    bmw = models.ForeignKey(User, null=True, blank=True)
    updated = models.DateTimeField(_('Updated'), auto_now=True)
    
    def __unicode__(self):
        return '%d-%d' % (self.fw_paper.id, self.fh_paper.id)
    
    class Meta:
        verbose_name = u'问卷差异'
        verbose_name_plural = u'问卷差异'
        
class QuestionDiff(models.Model):
    paper_diff = models.ForeignKey(PaperDiff)
    question = models.ForeignKey(Question)
    fw_q_score = models.FloatField(u'FW团队得分', null=True, blank=True)
    fw_q_comment = models.TextField(u'FW团队原因', max_length=1000, null=True, blank=True)
    fh_q_score = models.FloatField(u'复核团队得分', null=True, blank=True)
    fh_q_comment = models.TextField(u'复核团队原因', max_length=1000, null=True, blank=True)
    final_q_score = models.FloatField(u'BMW判决得分', null=True, blank=True)
    final_q_comment = models.TextField(u'BMW判决原因', max_length=1000, null=True, blank=True)
    marked = models.BooleanField(u'该差异是否已经审核过', default=False)
    updated = models.DateTimeField(_('Updated'), auto_now=True)
    
    def __unicode__(self):
        return '%d-%d' % (self.paper_diff.id, self.question.id)
    
    class Meta:
        verbose_name = u'问题差异'
        verbose_name_plural = u'问题差异'

class OtherReport(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    visitor_num = models.IntegerField(u'进店人数', null=True, blank=True)
    newold = models.BooleanField(u'新店', default=False)
    report_type = models.CharField(u'报告类型', max_length=50)
    term = models.ForeignKey(Term)
    dealertype = models.ForeignKey(DealerType, null=True, blank=True)
    dealer_num = models.IntegerField(u'经销商数量', null=True, blank=True)
    max_score = models.FloatField(u'最高分', null=True, blank=True)
    min_score = models.FloatField(u'最低分', null=True, blank=True)
    ave_score = models.FloatField(u'平均分', null=True, blank=True)
    
    def __unicode__(self):
        return '%s' % self.term.name_cn
    
    class Meta:
        verbose_name = _('OtherReport')

