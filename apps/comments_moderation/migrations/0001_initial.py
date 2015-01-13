# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'EmailFilter'
        db.create_table(u'comments_moderation_emailfilter', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')()),
        ))
        db.send_create_signal(u'comments_moderation', ['EmailFilter'])


    def backwards(self, orm):
        # Deleting model 'EmailFilter'
        db.delete_table(u'comments_moderation_emailfilter')


    models = {
        u'comments_moderation.emailfilter': {
            'Meta': {'object_name': 'EmailFilter'},
            'active': ('django.db.models.fields.BooleanField', [], {}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['comments_moderation']