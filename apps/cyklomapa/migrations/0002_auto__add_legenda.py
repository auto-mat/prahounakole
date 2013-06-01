# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Legenda'
        db.create_table('cyklomapa_legenda', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nazev', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50)),
            ('popis', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('obrazek', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
        ))
        db.send_create_signal('cyklomapa', ['Legenda'])


    def backwards(self, orm):
        # Deleting model 'Legenda'
        db.delete_table('cyklomapa_legenda')


    models = {
        'cyklomapa.legenda': {
            'Meta': {'object_name': 'Legenda'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nazev': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'obrazek': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'popis': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'})
        },
        'cyklomapa.poi': {
            'Meta': {'object_name': 'Poi'},
            'desc': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'desc_extra': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'dulezitost': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'foto_thumb': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'geom': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nazev': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'remark': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyklomapa.Status']"}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'znacka': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyklomapa.Znacka']"})
        },
        'cyklomapa.status': {
            'Meta': {'object_name': 'Status'},
            'desc': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nazev': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'show': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'show_TU': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'cyklomapa.upresneni': {
            'Meta': {'object_name': 'Upresneni'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'desc': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'misto': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyklomapa.Poi']", 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'cyklomapa.vrstva': {
            'Meta': {'ordering': "['order']", 'object_name': 'Vrstva'},
            'desc': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nazev': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'remark': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyklomapa.Status']"})
        },
        'cyklomapa.znacka': {
            'Meta': {'object_name': 'Znacka'},
            'default_icon': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True'}),
            'desc': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'maxzoom': ('django.db.models.fields.PositiveIntegerField', [], {'default': '10'}),
            'minzoom': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'nazev': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'remark': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyklomapa.Status']"}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'vrstva': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cyklomapa.Vrstva']"})
        }
    }

    complete_apps = ['cyklomapa']