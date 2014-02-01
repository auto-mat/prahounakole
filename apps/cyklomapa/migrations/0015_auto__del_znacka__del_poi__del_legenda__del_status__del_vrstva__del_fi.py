# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Znacka'
        db.delete_table(u'cyklomapa_znacka')

        # Deleting model 'Poi'
        db.delete_table(u'cyklomapa_poi')

        # Deleting model 'Legenda'
        db.delete_table(u'cyklomapa_legenda')

        # Deleting model 'Status'
        db.delete_table(u'cyklomapa_status')

        # Deleting model 'Vrstva'
        db.delete_table(u'cyklomapa_vrstva')

        # Deleting field 'Mesto.slug'
        db.delete_column(u'cyklomapa_mesto', 'slug')

        # Deleting field 'Mesto.nazev'
        db.delete_column(u'cyklomapa_mesto', 'nazev')


        # Changing field 'Upresneni.misto'
        db.alter_column(u'cyklomapa_upresneni', 'misto_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['webmap.Poi'], null=True))

    def backwards(self, orm):
        # Adding model 'Znacka'
        db.create_table(u'cyklomapa_znacka', (
            ('line_color', self.gf('colorful.fields.RGBColorField')(default='#ffc90e', max_length=7)),
            ('status', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyklomapa.Status'])),
            ('nazev', self.gf('django.db.models.fields.CharField')(max_length=255, unique=True)),
            ('minzoom', self.gf('django.db.models.fields.PositiveIntegerField')(default=1)),
            ('maxzoom', self.gf('django.db.models.fields.PositiveIntegerField')(default=10)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('desc', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('line_width', self.gf('django.db.models.fields.FloatField')(default=2)),
            ('remark', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('vrstva', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyklomapa.Vrstva'])),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, unique=True)),
            ('default_icon', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal(u'cyklomapa', ['Znacka'])

        # Adding model 'Poi'
        db.create_table(u'cyklomapa_poi', (
            ('status', self.gf('django.db.models.fields.related.ForeignKey')(default=3, to=orm['cyklomapa.Status'])),
            ('dulezitost', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('mesto', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['cyklomapa.Mesto'])),
            ('nazev', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('datum_zmeny', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('desc_extra', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('foto_thumb', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('desc', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('remark', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('znacka', self.gf('django.db.models.fields.related.ForeignKey')(related_name='pois', to=orm['cyklomapa.Znacka'])),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('geom', self.gf('django.contrib.gis.db.models.fields.GeometryField')()),
        ))
        db.send_create_signal(u'cyklomapa', ['Poi'])

        # Adding model 'Legenda'
        db.create_table(u'cyklomapa_legenda', (
            ('obrazek', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nazev', self.gf('django.db.models.fields.CharField')(max_length=255, unique=True)),
            ('popis', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, unique=True)),
        ))
        db.send_create_signal(u'cyklomapa', ['Legenda'])

        # Adding model 'Status'
        db.create_table(u'cyklomapa_status', (
            ('show', self.gf('django.db.models.fields.BooleanField')()),
            ('nazev', self.gf('django.db.models.fields.CharField')(max_length=255, unique=True)),
            ('show_TU', self.gf('django.db.models.fields.BooleanField')()),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('desc', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'cyklomapa', ['Status'])

        # Adding model 'Vrstva'
        db.create_table(u'cyklomapa_vrstva', (
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('status', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyklomapa.Status'])),
            ('remark', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=1, unique=True)),
            ('nazev', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')()),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('desc', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'cyklomapa', ['Vrstva'])

        # Adding field 'Mesto.slug'
        db.add_column(u'cyklomapa_mesto', 'slug',
                      self.gf('django.db.models.fields.SlugField')(default='', max_length=50, unique=True),
                      keep_default=False)

        # Adding field 'Mesto.nazev'
        db.add_column(u'cyklomapa_mesto', 'nazev',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, unique=True),
                      keep_default=False)


        # Changing field 'Upresneni.misto'
        db.alter_column(u'cyklomapa_upresneni', 'misto_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cyklomapa.Poi'], null=True))

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
        u'cyklomapa.markerznacka': {
            'Meta': {'object_name': 'MarkerZnacka'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'marker': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['webmap.Marker']", 'unique': 'True', 'null': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        u'cyklomapa.mesto': {
            'Meta': {'object_name': 'Mesto'},
            'aktivni': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'geom': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sektor': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['webmap.Sector']", 'unique': 'True', 'null': 'True'}),
            'uvodni_zprava': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'vyhledavani': ('django.db.models.fields.BooleanField', [], {}),
            'zoom': ('django.db.models.fields.PositiveIntegerField', [], {'default': '13'})
        },
        u'cyklomapa.upresneni': {
            'Meta': {'object_name': 'Upresneni'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'desc': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'misto': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['webmap.Poi']", 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        u'cyklomapa.usermesto': {
            'Meta': {'object_name': 'UserMesto'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mesta': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['cyklomapa.Mesto']", 'symmetrical': 'False'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        },
        u'webmap.layer': {
            'Meta': {'ordering': "['order']", 'object_name': 'Layer'},
            'desc': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '-1'}),
            'remark': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['webmap.Status']"})
        },
        u'webmap.marker': {
            'Meta': {'ordering': "['-layer__order', 'name']", 'object_name': 'Marker'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'default_icon': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'desc': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modification': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'layer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['webmap.Layer']"}),
            'line_color': ('colorful.fields.RGBColorField', [], {'default': "'#ffc90e'", 'max_length': '7'}),
            'line_width': ('django.db.models.fields.FloatField', [], {'default': '2'}),
            'maxzoom': ('django.db.models.fields.PositiveIntegerField', [], {'default': '10'}),
            'menu_icon': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'minzoom': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'remark': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'unique': 'True', 'null': 'True'}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['webmap.Status']"})
        },
        u'webmap.poi': {
            'Meta': {'object_name': 'Poi'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'author': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'poi_create'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'desc': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'desc_extra': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'geom': ('django.contrib.gis.db.models.fields.GeometryField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'importance': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'last_modification': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'marker': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'pois'", 'to': u"orm['webmap.Marker']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'properties': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['webmap.Property']", 'null': 'True', 'blank': 'True'}),
            'properties_cache': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'remark': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'default': '2', 'to': u"orm['webmap.Status']"}),
            'updated_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'poi_update'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        u'webmap.property': {
            'Meta': {'object_name': 'Property'},
            'as_filter': ('django.db.models.fields.BooleanField', [], {}),
            'default_icon': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'desc': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '-1'}),
            'remark': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['webmap.Status']"})
        },
        u'webmap.sector': {
            'Meta': {'object_name': 'Sector'},
            'geom': ('django.contrib.gis.db.models.fields.PolygonField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'})
        },
        u'webmap.status': {
            'Meta': {'object_name': 'Status'},
            'desc': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'show': ('django.db.models.fields.BooleanField', [], {}),
            'show_to_mapper': ('django.db.models.fields.BooleanField', [], {})
        }
    }

    complete_apps = ['cyklomapa']