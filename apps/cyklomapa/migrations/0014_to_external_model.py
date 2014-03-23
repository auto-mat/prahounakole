# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        "Write your forwards methods here."
        # Note: Don't use "from appname.models import ModelName". 
        # Use orm.ModelName to refer to models in this application,
        # and orm['appname.ModelName'] for models in other applications.
         
        license = orm['webmap.license'](name="bez licence")
        license.save()

        for obj in orm.status.objects.all():
            obj_new, created = orm['webmap.status'].objects.get_or_create(name = obj.nazev, 
                    defaults={
                        'id':             obj.id,
                        'desc':           obj.desc,
                        'show':           obj.show,
                        'show_to_mapper': obj.show_TU,
                    }
                )
            obj_new.save()

        for obj in orm.legenda.objects.all():
            obj_new, created = orm['webmap.legend'].objects.get_or_create(slug= obj.slug, 
                    defaults={
                        'id':             obj.id,
                        'name':           obj.nazev,
                        'slug':           obj.slug,
                        'desc':           obj.popis,
                        'image':          obj.obrazek,
                    }
                )
            obj_new.save()

        for obj in orm.vrstva.objects.all():
            obj_new, created = orm['webmap.layer'].objects.get_or_create(slug= obj.slug, 
                    defaults={
                        'id':             obj.id,
                        'name':           obj.nazev,
                        'slug':           obj.slug,
                        'desc':           obj.desc,
                        'status':         orm['webmap.status'].objects.get(name= obj.status.nazev),
                        'order':          obj.order,
                        'remark':         obj.remark,
                        'enabled':        obj.enabled,
                    }
                )
            obj_new.save()

        for obj in orm.znacka.objects.all():
            obj_new, created = orm['webmap.marker'].objects.get_or_create(name = obj.nazev,
                    defaults={
                        'id':             obj.id,
                        'layer':          orm['webmap.layer'].objects.get(slug= obj.vrstva.slug),
                        'status':         orm['webmap.status'].objects.get(name= obj.status.nazev),
                        'desc':           obj.desc,
                        'remark':         obj.remark,
                        'default_icon':   obj.default_icon,
                        'minzoom':        obj.minzoom,
                        'maxzoom':        obj.maxzoom,
                        'slug':           obj.slug,
                        'line_width':     obj.line_width,
                        'line_color':     obj.line_color,
                    }
                )
            obj_new.save()
            markerznacka = orm.markerznacka( url = obj.url, marker = obj_new )
            markerznacka.save()

        for obj in orm.mesto.objects.all():
            obj_new, created = orm['webmap.sector'].objects.get_or_create(slug = obj.slug,
                    defaults={
                        'id':             obj.id,
                        'name':           obj.nazev,
                        'slug':           obj.slug,
                        'geom':           "POLYGON ((14.0592378174430870 49.8937003767014176, 14.5234101806598481 49.8733483390246803, 14.8461335692865131 49.9909175906933356, 14.8227876220244426 50.1970728989478943, 14.5604890380763354 50.2796378092465019, 14.1855805908628714 50.2743719806893949, 13.9974397217486395 50.1073193726645556, 14.0592378174430870 49.8937003767014176))",
                    }
                )
            obj_new.save()
            obj.sektor = obj_new
            obj.save()

        poi_objects = orm.poi.objects
        i = 0.0
        for obj in poi_objects.all():
            if i % 1000 == 0:
               print i
            i += 1
            for field in obj_new._meta.local_fields:
                if field.name == "last_modification":
                    field.auto_now = False
                elif field.name == "created_at":
                    field.auto_now_add = False

            kwargs={
                'id':             obj.id,
                'name':           obj.nazev,
                'marker':         orm['webmap.marker'].objects.get(name=obj.znacka.nazev),
                'status':         orm['webmap.status'].objects.get(name= obj.status.nazev),
                'importance':     obj.dulezitost,
                'geom':           obj.geom,
                'desc':           obj.desc,
                'desc_extra':     obj.desc_extra,
                'url':            obj.url,
                'remark':         obj.remark,
                'last_modification':     obj.datum_zmeny,
                'created_at':     obj.datum_zmeny,
            }

            obj_new = orm['webmap.poi'].objects.create(**kwargs)

            if obj.foto_thumb:
                photo_new = orm['webmap.photo'].objects.create(poi = obj_new, photo = obj.foto_thumb, license=license, order=0)
                photo_new.save()

    def backwards(self, orm):
        "Write your backwards methods here."
        orm['webmap.photo'].objects.all().delete()
        orm['webmap.poi'].objects.all().delete()
        orm['webmap.status'].objects.all().delete()
        orm['webmap.marker'].objects.all().delete()
        orm['webmap.layer'].objects.all().delete()
        #orm['webmap.sector'].objects.all().delete()


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
        'webmap.layer': {
            'Meta': {'ordering': "['order']", 'object_name': 'Layer'},
            'desc': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'remark': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['webmap.Status']"})
        },
        'webmap.license': {
            'Meta': {'object_name': 'License'},
            'desc': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'webmap.marker': {
            'Meta': {'ordering': "['-layer__order', 'name']", 'object_name': 'Marker'},
            'default_icon': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'desc': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'layer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['webmap.Layer']"}),
            'line_color': ('colorful.fields.RGBColorField', [], {'default': "'#ffc90e'", 'max_length': '7'}),
            'line_width': ('django.db.models.fields.FloatField', [], {'default': '2'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'unique': 'True', 'null': 'True'}),
            'maxzoom': ('django.db.models.fields.PositiveIntegerField', [], {'default': '10'}),
            'minzoom': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'remark': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['webmap.Status']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True', 'default': 'datetime.datetime.now'}),
            'last_modification': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True', 'default': 'datetime.datetime.now'}),
        },
        'webmap.photo': {
            'Meta': {'object_name': 'Photo'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'photo_create'", 'null': 'True', 'to': "orm['auth.User']"}),
            'desc': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'license': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['webmap.License']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'photo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'photographer': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'poi': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'photos'", 'to': "orm['webmap.Poi']"}),
            'updated_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'photo_update'", 'null': 'True', 'to': "orm['auth.User']"})
        },
        'webmap.poi': {
            'Meta': {'object_name': 'Poi'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'author': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'poi_create'", 'null': 'True', 'to': "orm['auth.User']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'desc': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'desc_extra': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'geom': ('django.contrib.gis.db.models.fields.GeometryField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'importance': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'last_modification': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'marker': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'pois'", 'to': "orm['webmap.Marker']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'properties': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['webmap.Property']", 'null': 'True', 'blank': 'True'}),
            'properties_cache': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'remark': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'default': '2', 'to': "orm['webmap.Status']"}),
            'updated_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'poi_update'", 'null': 'True', 'to': "orm['auth.User']"}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'webmap.property': {
            'Meta': {'ordering': "['order']", 'object_name': 'Property'},
            'as_filter': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'default_icon': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'desc': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'remark': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['webmap.Status']"})
        },
        'webmap.sector': {
            'Meta': {'object_name': 'Sector'},
            'geom': ('django.contrib.gis.db.models.fields.PolygonField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'})
        },
        u'webmap.legend': {
            'Meta': {'object_name': 'Legend'},
            'desc': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'})
        },
        'webmap.status': {
            'Meta': {'object_name': 'Status'},
            'desc': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'show': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'show_to_mapper': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'cyklomapa.legenda': {
            'Meta': {'object_name': 'Legenda'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nazev': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'obrazek': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'popis': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'})
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
            'nazev': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'sektor': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['webmap.Sector']", 'unique': 'True', 'null': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'uvodni_zprava': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'vyhledavani': ('django.db.models.fields.BooleanField', [], {}),
            'zoom': ('django.db.models.fields.PositiveIntegerField', [], {'default': '13'})
        },
        u'cyklomapa.poi': {
            'Meta': {'object_name': 'Poi'},
            'datum_zmeny': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'desc': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'desc_extra': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'dulezitost': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'foto_thumb': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'geom': ('django.contrib.gis.db.models.fields.GeometryField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mesto': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': u"orm['cyklomapa.Mesto']"}),
            'nazev': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'remark': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'default': '3', 'to': u"orm['cyklomapa.Status']"}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'znacka': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'pois'", 'to': u"orm['cyklomapa.Znacka']"})
        },
        u'cyklomapa.status': {
            'Meta': {'object_name': 'Status'},
            'desc': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nazev': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'show': ('django.db.models.fields.BooleanField', [], {}),
            'show_TU': ('django.db.models.fields.BooleanField', [], {})
        },
        u'cyklomapa.upresneni': {
            'Meta': {'object_name': 'Upresneni'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'desc': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'misto': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cyklomapa.Poi']", 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        u'cyklomapa.usermesto': {
            'Meta': {'object_name': 'UserMesto'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mesta': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['cyklomapa.Mesto']", 'symmetrical': 'False'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        },
        u'cyklomapa.vrstva': {
            'Meta': {'ordering': "['order']", 'object_name': 'Vrstva'},
            'desc': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nazev': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'remark': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '1'}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cyklomapa.Status']"})
        },
        u'cyklomapa.znacka': {
            'Meta': {'ordering': "['-vrstva__order', 'nazev']", 'object_name': 'Znacka'},
            'default_icon': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'desc': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'line_color': ('colorful.fields.RGBColorField', [], {'default': "'#ffc90e'", 'max_length': '7'}),
            'line_width': ('django.db.models.fields.FloatField', [], {'default': '2'}),
            'maxzoom': ('django.db.models.fields.PositiveIntegerField', [], {'default': '10'}),
            'minzoom': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'nazev': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'remark': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cyklomapa.Status']"}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'vrstva': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cyklomapa.Vrstva']"})
        }
    }

    complete_apps = ['webmap', 'cyklomapa']
    symmetrical = True
