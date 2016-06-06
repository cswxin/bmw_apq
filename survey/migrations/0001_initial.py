# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Project'
        db.create_table('survey_project', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('survey', ['Project'])

        # Adding model 'Question'
        db.create_table('survey_question', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.TextField')(max_length=10000, null=True, blank=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['survey.Project'], null=True, blank=True)),
            ('cid', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('questiontype', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('listorder', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('base_question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['survey.Question'], null=True, blank=True)),
            ('other_type', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('max_answer_num', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('survey', ['Question'])

        # Adding model 'QuestionQA'
        db.create_table('survey_questionqa', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['survey.Question'])),
            ('q_desc', self.gf('django.db.models.fields.TextField')(max_length=1000, null=True, blank=True)),
            ('a_desc', self.gf('django.db.models.fields.TextField')(max_length=1000, null=True, blank=True)),
            ('q_addon', self.gf('django.db.models.fields.TextField')(max_length=1000, null=True, blank=True)),
            ('q_desc_en', self.gf('django.db.models.fields.TextField')(max_length=1000, null=True, blank=True)),
            ('a_desc_en', self.gf('django.db.models.fields.TextField')(max_length=1000, null=True, blank=True)),
            ('q_addon_en', self.gf('django.db.models.fields.TextField')(max_length=1000, null=True, blank=True)),
            ('q_en', self.gf('django.db.models.fields.TextField')(max_length=1000, null=True, blank=True)),
        ))
        db.send_create_signal('survey', ['QuestionQA'])

        # Adding model 'QuestionAttribute'
        db.create_table('survey_questionattribute', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['survey.Question'], null=True, blank=True)),
            ('attr_name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('attr_value', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
        ))
        db.send_create_signal('survey', ['QuestionAttribute'])

        # Adding model 'Alternative'
        db.create_table('survey_alternative', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.TextField')(max_length=1000, null=True, blank=True)),
            ('cid', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['survey.Question'], null=True, blank=True)),
            ('open', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('listorder', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('score', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('survey', ['Alternative'])

        # Adding model 'AlternativeAttribute'
        db.create_table('survey_alternativeattribute', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('alternative', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['survey.Alternative'], null=True, blank=True)),
            ('attr_name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('attr_value', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
        ))
        db.send_create_signal('survey', ['AlternativeAttribute'])

        # Adding model 'MatrixRow'
        db.create_table('survey_matrixrow', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.TextField')(max_length=1000, null=True, blank=True)),
            ('cid', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['survey.Question'], null=True, blank=True)),
            ('listorder', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('survey', ['MatrixRow'])

        # Adding model 'MatrixRowAttribute'
        db.create_table('survey_matrixrowattribute', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('matrixrow', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['survey.MatrixRow'], null=True, blank=True)),
            ('attr_name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('attr_value', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
        ))
        db.send_create_signal('survey', ['MatrixRowAttribute'])

        # Adding model 'Validator'
        db.create_table('survey_validator', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('func', self.gf('django.db.models.fields.TextField')(max_length=1000, null=True, blank=True)),
            ('error_tip', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('desc', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
        ))
        db.send_create_signal('survey', ['Validator'])

        # Adding model 'InputValidator'
        db.create_table('survey_inputvalidator', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['survey.Question'], null=True, blank=True)),
            ('alternative', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['survey.Alternative'], null=True, blank=True)),
            ('matrixrow', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['survey.MatrixRow'], null=True, blank=True)),
            ('min', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('max', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('validator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['survey.Validator'], null=True, blank=True)),
        ))
        db.send_create_signal('survey', ['InputValidator'])

        # Adding model 'Respondent'
        db.create_table('survey_respondent', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['survey.Project'], null=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('finish_time', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('survey', ['Respondent'])

        # Adding model 'CheckPoint'
        db.create_table('survey_checkpoint', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('name_abbr', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('desc', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('desc_en', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['survey.Question'], null=True, blank=True)),
            ('alternative', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['survey.Alternative'], null=True, blank=True)),
            ('matrixrow', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['survey.MatrixRow'], null=True, blank=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['survey.CheckPoint'], null=True, blank=True)),
            ('has_child', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('resp_col', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
        ))
        db.send_create_signal('survey', ['CheckPoint'])

        # Adding model 'Translation'
        db.create_table('survey_translation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('respondent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['survey.Respondent'], null=True, blank=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['survey.Project'], null=True, blank=True)),
            ('column_name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('content_en', self.gf('django.db.models.fields.TextField')(max_length=1000, null=True, blank=True)),
        ))
        db.send_create_signal('survey', ['Translation'])


    def backwards(self, orm):
        
        # Deleting model 'Project'
        db.delete_table('survey_project')

        # Deleting model 'Question'
        db.delete_table('survey_question')

        # Deleting model 'QuestionQA'
        db.delete_table('survey_questionqa')

        # Deleting model 'QuestionAttribute'
        db.delete_table('survey_questionattribute')

        # Deleting model 'Alternative'
        db.delete_table('survey_alternative')

        # Deleting model 'AlternativeAttribute'
        db.delete_table('survey_alternativeattribute')

        # Deleting model 'MatrixRow'
        db.delete_table('survey_matrixrow')

        # Deleting model 'MatrixRowAttribute'
        db.delete_table('survey_matrixrowattribute')

        # Deleting model 'Validator'
        db.delete_table('survey_validator')

        # Deleting model 'InputValidator'
        db.delete_table('survey_inputvalidator')

        # Deleting model 'Respondent'
        db.delete_table('survey_respondent')

        # Deleting model 'CheckPoint'
        db.delete_table('survey_checkpoint')

        # Deleting model 'Translation'
        db.delete_table('survey_translation')


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
        'survey.alternative': {
            'Meta': {'object_name': 'Alternative'},
            'cid': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'listorder': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'open': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.Question']", 'null': 'True', 'blank': 'True'}),
            'score': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.TextField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'survey.alternativeattribute': {
            'Meta': {'object_name': 'AlternativeAttribute'},
            'alternative': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.Alternative']", 'null': 'True', 'blank': 'True'}),
            'attr_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'attr_value': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'survey.checkpoint': {
            'Meta': {'object_name': 'CheckPoint'},
            'alternative': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.Alternative']", 'null': 'True', 'blank': 'True'}),
            'desc': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'desc_en': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'has_child': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'matrixrow': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.MatrixRow']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'name_abbr': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.CheckPoint']", 'null': 'True', 'blank': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.Question']", 'null': 'True', 'blank': 'True'}),
            'resp_col': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'})
        },
        'survey.inputvalidator': {
            'Meta': {'object_name': 'InputValidator'},
            'alternative': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.Alternative']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'matrixrow': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.MatrixRow']", 'null': 'True', 'blank': 'True'}),
            'max': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'min': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.Question']", 'null': 'True', 'blank': 'True'}),
            'validator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.Validator']", 'null': 'True', 'blank': 'True'})
        },
        'survey.matrixrow': {
            'Meta': {'object_name': 'MatrixRow'},
            'cid': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'listorder': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.Question']", 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.TextField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'survey.matrixrowattribute': {
            'Meta': {'object_name': 'MatrixRowAttribute'},
            'attr_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'attr_value': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'matrixrow': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.MatrixRow']", 'null': 'True', 'blank': 'True'})
        },
        'survey.project': {
            'Meta': {'object_name': 'Project'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'survey.question': {
            'Meta': {'object_name': 'Question'},
            'base_question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.Question']", 'null': 'True', 'blank': 'True'}),
            'cid': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'listorder': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'max_answer_num': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'other_type': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.Project']", 'null': 'True', 'blank': 'True'}),
            'questiontype': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.TextField', [], {'max_length': '10000', 'null': 'True', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'survey.questionattribute': {
            'Meta': {'object_name': 'QuestionAttribute'},
            'attr_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'attr_value': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.Question']", 'null': 'True', 'blank': 'True'})
        },
        'survey.questionqa': {
            'Meta': {'object_name': 'QuestionQA'},
            'a_desc': ('django.db.models.fields.TextField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'a_desc_en': ('django.db.models.fields.TextField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'q_addon': ('django.db.models.fields.TextField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'q_addon_en': ('django.db.models.fields.TextField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'q_desc': ('django.db.models.fields.TextField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'q_desc_en': ('django.db.models.fields.TextField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'q_en': ('django.db.models.fields.TextField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.Question']"})
        },
        'survey.respondent': {
            'Meta': {'object_name': 'Respondent'},
            'finish_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.Project']", 'null': 'True', 'blank': 'True'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'survey.translation': {
            'Meta': {'object_name': 'Translation'},
            'column_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'content_en': ('django.db.models.fields.TextField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.Project']", 'null': 'True', 'blank': 'True'}),
            'respondent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.Respondent']", 'null': 'True', 'blank': 'True'})
        },
        'survey.validator': {
            'Meta': {'object_name': 'Validator'},
            'desc': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'error_tip': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'func': ('django.db.models.fields.TextField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['survey']
