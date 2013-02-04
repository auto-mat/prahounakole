# -*- coding: utf-8 -*-
# admin.py

# This file controls the look and feel of the models within the Admin App
# They appear in the admin app once they are registered at the bottom of 
# this code (same goes for the databrowse app)

from django.conf import settings # needed if we use the GOOGLE_MAPS_API_KEY from settings

# Import the admin site reference from django.contrib.admin
from django.contrib import admin

# Grab the Admin Manager that automaticall initializes an OpenLayers map
# for any geometry field using the in Google Mercator projection with OpenStreetMap basedata
from django.contrib.gis.admin import OSMGeoAdmin

from cyklomapa.models import *

USE_GOOGLE_TERRAIN_TILES = False

class PoiAdmin(OSMGeoAdmin):
    # Standard Django Admin Options
    # http://docs.djangoproject.com/en/1.1/ref/contrib/admin/
    list_display = ('__unicode__', 'nazev','status','znacka','url','foto_thumb')
    list_filter = ('mesto__nazev', 'znacka__vrstva', 'znacka', 'status',)
    search_fields = ('nazev',)
    ordering = ('nazev',)
    save_as = True
    search_fields = ['nazev']
    list_select_related = True

    if USE_GOOGLE_TERRAIN_TILES:
      map_template = 'gis/admin/google.html'
      extra_js = ['http://openstreetmap.org/openlayers/OpenStreetMap.js', 'http://maps.google.com/maps?file=api&amp;v=2&amp;key=%s' % settings.GOOGLE_MAPS_API_KEY]
    else:
      pass # defaults to OSMGeoAdmin presets of OpenStreetMap tiles

    # Default GeoDjango OpenLayers map options
    # Uncomment and modify as desired
    # To learn more about this jargon visit:
    # www.openlayers.org
    
    default_lon = 1605350
    default_lat = 6461466
    default_zoom = 12
    #display_wkt = False
    #display_srid = False
    #extra_js = []
    #num_zoom = 18
    #max_zoom = False
    #min_zoom = False
    #units = False
    #max_resolution = False
    #max_extent = False
    #modifiable = True
    #mouse_position = True
    #scale_text = True
    #layerswitcher = True
    scrollable = False
    map_width = 700
    map_height = 500
    map_srid = 900913
    #map_template = 'gis/admin/openlayers.html'
    #openlayers_url = 'http://openlayers.org/api/2.6/OpenLayers.js'
    #wms_url = 'http://labs.metacarta.com/wms/vmap0'
    #wms_layer = 'basic'
    #wms_name = 'OpenLayers WMS'
    #debug = False
    #widget = OpenLayersWidget

class ZnackaInline(admin.TabularInline):
    model = Znacka

class VrstvaAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('nazev',) } # slug se automaticky vytvari z nazvu
    list_display = ['nazev', 'status', 'order']
    inlines = [ZnackaInline]

class ZnackaAdmin(admin.ModelAdmin):
    list_display = ('nazev', 'vrstva', 'minzoom', 'status')
    list_filter = ('vrstva','status',)
    search_fields = ('nazev',)
    
class UpresneniAdmin(admin.ModelAdmin):
    model = Upresneni
    raw_id_fields = ('misto',)
    list_filter = ('status',)
    list_display = ('misto', 'email', 'status', 'desc',)

class LegendaAdmin(admin.ModelAdmin):
    list_display = ('nazev', 'obrazek_img', 'popis',)
    def obrazek_img(self, obj):
        return u'<img src=%s>' % obj.obrazek.url
    obrazek_img.allow_tags = True
    obrazek_img.short_description = u"obrázek"

class MestoAdmin(OSMGeoAdmin):
   list_display = ('nazev', 'slug', 'vyhledavani', 'zoom', 'uvodni_zprava',)
   if USE_GOOGLE_TERRAIN_TILES:
     map_template = 'gis/admin/google.html'
     extra_js = ['http://openstreetmap.org/openlayers/OpenStreetMap.js', 'http://maps.google.com/maps?file=api&amp;v=2&amp;key=%s' % settings.GOOGLE_MAPS_API_KEY]
   else:
     pass # defaults to OSMGeoAdmin presets of OpenStreetMap tiles
   
   default_lon = 1605350
   default_lat = 6461466
   default_zoom = 12
   scrollable = False
   map_width = 700
   map_height = 500
   map_srid = 900913

admin.site.register(Poi   , PoiAdmin   )
admin.site.register(Vrstva, VrstvaAdmin)
admin.site.register(Znacka, ZnackaAdmin)
admin.site.register(Status, admin.ModelAdmin)
admin.site.register(Upresneni, UpresneniAdmin)
admin.site.register(Legenda, LegendaAdmin)
admin.site.register(Mesto, MestoAdmin)
