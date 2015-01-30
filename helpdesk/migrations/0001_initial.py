# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Project'
        db.create_table(u'helpdesk_project', (
            ('machine_name', self.gf('django.db.models.fields.CharField')(max_length=64, primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal(u'helpdesk', ['Project'])

        # Adding model 'State'
        db.create_table(u'helpdesk_state', (
            ('machine_name', self.gf('django.db.models.fields.CharField')(max_length=32, primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('resolved', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'helpdesk', ['State'])

        # Adding model 'Ticket'
        db.create_table(u'helpdesk_ticket', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('body', self.gf('django.db.models.fields.TextField')()),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['helpdesk.Project'])),
            ('state', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['helpdesk.State'])),
            ('priority', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('assignee', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('customer', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('message_id', self.gf('django.db.models.fields.CharField')(unique=True, max_length=256)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'helpdesk', ['Ticket'])


    def backwards(self, orm):
        # Deleting model 'Project'
        db.delete_table(u'helpdesk_project')

        # Deleting model 'State'
        db.delete_table(u'helpdesk_state')

        # Deleting model 'Ticket'
        db.delete_table(u'helpdesk_ticket')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'helpdesk.project': {
            'Meta': {'object_name': 'Project'},
            'machine_name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        u'helpdesk.state': {
            'Meta': {'object_name': 'State'},
            'machine_name': ('django.db.models.fields.CharField', [], {'max_length': '32', 'primary_key': 'True'}),
            'resolved': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        u'helpdesk.ticket': {
            'Meta': {'object_name': 'Ticket'},
            'assignee': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'body': ('django.db.models.fields.TextField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'customer': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '256'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['helpdesk.Project']"}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['helpdesk.State']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['helpdesk']