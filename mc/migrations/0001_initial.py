# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Province'
        db.create_table('mc_province', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
        ))
        db.send_create_signal('mc', ['Province'])

        # Adding model 'City'
        db.create_table('mc_city', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('province', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mc.Province'], null=True, blank=True)),
            ('sn', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('mc', ['City'])

        # Adding model 'Term'
        db.create_table('mc_term', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('name_cn', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('name_en', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('begin', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_active_input', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('end', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('listorder', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('mc', ['Term'])

        # Adding model 'DealerType'
        db.create_table('mc_dealertype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name_cn', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('name_en', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
        ))
        db.send_create_signal('mc', ['DealerType'])

        # Adding model 'Dealer'
        db.create_table('mc_dealer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('dealertype', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mc.DealerType'], null=True, blank=True)),
            ('name_cn', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('name_en', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('abbr_cn', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('abbr_en', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('city_cn', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('city_en', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('province_cn', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('province_en', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('tel', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mc.Dealer'], null=True, blank=True)),
            ('has_child', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('listorder', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('mc', ['Dealer'])

        # Adding model 'DealerPosition'
        db.create_table('mc_dealerposition', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('dealer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mc.Dealer'], null=True, blank=True)),
            ('term', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mc.Term'], null=True, blank=True)),
            ('position_region', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('count_region', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('position_nation', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('count_nation', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('Total', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
        ))
        db.send_create_signal('mc', ['DealerPosition'])

        # Adding model 'Report'
        db.create_table('mc_report', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('respondent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['survey.Respondent'], null=True, blank=True)),
            ('dealer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mc.Dealer'], null=True, blank=True)),
            ('dealer_name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('dealertype', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mc.DealerType'], null=True, blank=True)),
            ('term', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mc.Term'], null=True, blank=True)),
            ('term_name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('score', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('is_public', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('mc', ['Report'])

        # Adding model 'DealerVisitor'
        db.create_table('mc_dealervisitor', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('dealer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mc.Dealer'], null=True, blank=True)),
            ('term', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mc.Term'], null=True, blank=True)),
            ('plan_begin', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('plan_end', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('respondent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['survey.Respondent'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('mc', ['DealerVisitor'])

        # Adding model 'DealerManager'
        db.create_table('mc_dealermanager', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('dealer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mc.Dealer'], null=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
        ))
        db.send_create_signal('mc', ['DealerManager'])

        # Adding model 'ReportDocument'
        db.create_table('mc_reportdocument', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('term', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mc.Term'], null=True, blank=True)),
            ('document', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('areacode', self.gf('django.db.models.fields.IntegerField')(default=1)),
        ))
        db.send_create_signal('mc', ['ReportDocument'])

        # Adding model 'Paper'
        db.create_table('mc_paper', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('survey_code', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('respondent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['survey.Respondent'], null=True, blank=True)),
            ('dealer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mc.Dealer'], null=True, blank=True)),
            ('term', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mc.Term'], null=True, blank=True)),
            ('visit_begin', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('visit_end', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('score', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('is_public', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('mc', ['Paper'])

        # Adding unique constraint on 'Paper', fields ['dealer', 'term']
        db.create_unique('mc_paper', ['dealer_id', 'term_id'])

        # Adding model 'ReportSound'
        db.create_table('mc_reportsound', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('paper', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mc.Paper'])),
            ('sound', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_modify', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('mc', ['ReportSound'])

        # Adding model 'ReportImage'
        db.create_table('mc_reportimage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('paper', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mc.Paper'])),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_modify', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('mc', ['ReportImage'])

        # Adding model 'XslReport'
        db.create_table('mc_xslreport', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('paper', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mc.Paper'], null=True, blank=True)),
            ('xslfile', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal('mc', ['XslReport'])

        # Adding model 'XlsReportHist'
        db.create_table('mc_xlsreporthist', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('dealer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mc.Dealer'], null=True, blank=True)),
            ('term_index', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('xlsfile', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('score', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
        ))
        db.send_create_signal('mc', ['XlsReportHist'])

        # Adding model 'PaperAudit'
        db.create_table('mc_paperaudit', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('paper', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mc.Paper'], null=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('old_status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('new_status', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
        ))
        db.send_create_signal('mc', ['PaperAudit'])

        # Adding model 'PaperAuditItem'
        db.create_table('mc_paperaudititem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('paperaudit', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mc.PaperAudit'], null=True, blank=True)),
            ('question_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('old_answer', self.gf('django.db.models.fields.TextField')(max_length=10000, null=True, blank=True)),
            ('new_answer', self.gf('django.db.models.fields.TextField')(max_length=10000, null=True, blank=True)),
            ('valid', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('mc', ['PaperAuditItem'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Paper', fields ['dealer', 'term']
        db.delete_unique('mc_paper', ['dealer_id', 'term_id'])

        # Deleting model 'Province'
        db.delete_table('mc_province')

        # Deleting model 'City'
        db.delete_table('mc_city')

        # Deleting model 'Term'
        db.delete_table('mc_term')

        # Deleting model 'DealerType'
        db.delete_table('mc_dealertype')

        # Deleting model 'Dealer'
        db.delete_table('mc_dealer')

        # Deleting model 'DealerPosition'
        db.delete_table('mc_dealerposition')

        # Deleting model 'Report'
        db.delete_table('mc_report')

        # Deleting model 'DealerVisitor'
        db.delete_table('mc_dealervisitor')

        # Deleting model 'DealerManager'
        db.delete_table('mc_dealermanager')

        # Deleting model 'ReportDocument'
        db.delete_table('mc_reportdocument')

        # Deleting model 'Paper'
        db.delete_table('mc_paper')

        # Deleting model 'ReportSound'
        db.delete_table('mc_reportsound')

        # Deleting model 'ReportImage'
        db.delete_table('mc_reportimage')

        # Deleting model 'XslReport'
        db.delete_table('mc_xslreport')

        # Deleting model 'XlsReportHist'
        db.delete_table('mc_xlsreporthist')

        # Deleting model 'PaperAudit'
        db.delete_table('mc_paperaudit')

        # Deleting model 'PaperAuditItem'
        db.delete_table('mc_paperaudititem')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'mc.city': {
            'Meta': {'object_name': 'City'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'province': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mc.Province']", 'null': 'True', 'blank': 'True'}),
            'sn': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'mc.dealer': {
            'Meta': {'object_name': 'Dealer'},
            'abbr_cn': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'abbr_en': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'address': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'city_cn': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'city_en': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'dealertype': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mc.DealerType']", 'null': 'True', 'blank': 'True'}),
            'has_child': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'listorder': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'name_cn': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mc.Dealer']", 'null': 'True', 'blank': 'True'}),
            'province_cn': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'province_en': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'tel': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'mc.dealermanager': {
            'Meta': {'object_name': 'DealerManager'},
            'dealer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mc.Dealer']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'mc.dealerposition': {
            'Meta': {'object_name': 'DealerPosition'},
            'Total': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'count_nation': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'count_region': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'dealer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mc.Dealer']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'position_nation': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'position_region': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'term': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mc.Term']", 'null': 'True', 'blank': 'True'})
        },
        'mc.dealertype': {
            'Meta': {'object_name': 'DealerType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name_cn': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'})
        },
        'mc.dealervisitor': {
            'Meta': {'object_name': 'DealerVisitor'},
            'dealer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mc.Dealer']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'plan_begin': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'plan_end': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'respondent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.Respondent']", 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'term': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mc.Term']", 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'mc.paper': {
            'Meta': {'unique_together': "(('dealer', 'term'),)", 'object_name': 'Paper'},
            'dealer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mc.Dealer']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'respondent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.Respondent']", 'null': 'True', 'blank': 'True'}),
            'score': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'survey_code': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'term': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mc.Term']", 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'visit_begin': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'visit_end': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        'mc.paperaudit': {
            'Meta': {'object_name': 'PaperAudit'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'new_status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'old_status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'paper': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mc.Paper']", 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'mc.paperaudititem': {
            'Meta': {'object_name': 'PaperAuditItem'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'new_answer': ('django.db.models.fields.TextField', [], {'max_length': '10000', 'null': 'True', 'blank': 'True'}),
            'old_answer': ('django.db.models.fields.TextField', [], {'max_length': '10000', 'null': 'True', 'blank': 'True'}),
            'paperaudit': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mc.PaperAudit']", 'null': 'True', 'blank': 'True'}),
            'question_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'valid': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'mc.province': {
            'Meta': {'object_name': 'Province'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'})
        },
        'mc.report': {
            'Meta': {'object_name': 'Report'},
            'dealer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mc.Dealer']", 'null': 'True', 'blank': 'True'}),
            'dealer_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'dealertype': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mc.DealerType']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'respondent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.Respondent']", 'null': 'True', 'blank': 'True'}),
            'score': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'term': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mc.Term']", 'null': 'True', 'blank': 'True'}),
            'term_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'})
        },
        'mc.reportdocument': {
            'Meta': {'object_name': 'ReportDocument'},
            'areacode': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'document': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'term': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mc.Term']", 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'mc.reportimage': {
            'Meta': {'object_name': 'ReportImage'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'last_modify': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'paper': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mc.Paper']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'mc.reportsound': {
            'Meta': {'object_name': 'ReportSound'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modify': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'paper': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mc.Paper']"}),
            'sound': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'mc.term': {
            'Meta': {'object_name': 'Term'},
            'begin': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'end': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_active_input': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'listorder': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'name_cn': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'})
        },
        'mc.xlsreporthist': {
            'Meta': {'object_name': 'XlsReportHist'},
            'dealer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mc.Dealer']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'score': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'term_index': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'xlsfile': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        'mc.xslreport': {
            'Meta': {'object_name': 'XslReport'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'paper': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mc.Paper']", 'null': 'True', 'blank': 'True'}),
            'xslfile': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        'survey.project': {
            'Meta': {'object_name': 'Project'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'survey.respondent': {
            'Meta': {'object_name': 'Respondent'},
            'finish_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.Project']", 'null': 'True', 'blank': 'True'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['mc']
