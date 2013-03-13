# -*- coding: utf-8 -*-
# admin.py

# This file controls the look and feel of the models within the Admin App
# They appear in the admin app once they are registered at the bottom of 
# this code (same goes for the databrowse app)

from django.conf import settings # needed if we use the GOOGLE_MAPS_API_KEY from settings

# Import the admin site reference from django.contrib.admin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

# Grab the Admin Manager that automaticall initializes an OpenLayers map
# for any geometry field using the in Google Mercator projection with OpenStreetMap basedata
from django.contrib.gis.admin import OSMGeoAdmin
from django.contrib.gis.geos import Point

from cyklomapa.models import *

USE_GOOGLE_TERRAIN_TILES = False

# Define an inline admin descriptor for Employee model
# which acts a bit like a singleton
class UserMestoInline(admin.StackedInline):
    model = UserMesto
    can_delete = False
    verbose_name_plural = 'Uzivatelska mesta'

# Define a new User admin
class UserAdmin(UserAdmin):
    inlines = (UserMestoInline, )

class PoiAdmin(OSMGeoAdmin):
    def queryset(self, request):
       queryset = super(PoiAdmin, self).queryset(request)
       if request.user.is_superuser:
          return queryset

       return queryset.filter(mesto__in=request.user.usermesto.mesta.all())

    def get_form(self, request, obj=None, **kwargs):
         mesto = Mesto.objects.get(slug = request.subdomain)
         pnt = Point(mesto.geom.x, mesto.geom.y, srid=4326)
         pnt.transform(900913)
         self.default_lon, self.default_lat = pnt.coords

         form = super(PoiAdmin, self).get_form(request, obj, **kwargs)
         form.base_fields['mesto'].initial = mesto
         return form

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
       if db_field.name == "mesto":
          if request.user.is_superuser:
              kwargs["queryset"] = Mesto.objects
          else:
              kwargs["queryset"] = request.user.usermesto.mesta.all()

       return super(PoiAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def has_change_permission(self, request, obj = None):
       if request.user.is_superuser:
          return True
       if obj == None:
          return True
       return obj.mesto in request.user.usermesto.mesta.all()

    def has_delete_permission(self, request, obj = None):
       if request.user.is_superuser:
          return True
       if obj == None:
          return False
       return obj.mesto in request.user.usermesto.mesta.all()

    # Standard Django Admin Options
    # http://docs.djangoproject.com/en/1.1/ref/contrib/admin/
    list_display = ('__unicode__', 'nazev','status','znacka','url','foto_thumb', 'mesto', 'id')
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
   def queryset(self, request):
      queryset = super(MestoAdmin, self).queryset(request)
      if request.user.is_superuser:
         return queryset

      return queryset.filter(id__in=request.user.usermesto.mesta.all())

   def has_change_permission(self, request, obj = None):
      if request.user.is_superuser:
         return True
      if obj == None:
         return True
      return obj in request.user.usermesto.mesta.all()

   def get_form(self, request, obj=None, **kwargs):
       if request.user.is_superuser:
           self.exclude = ()
       else:
           self.exclude = ('slug', 'vyhledavani', 'aktivni',)  
       return super(MestoAdmin, self).get_form(request, obj=None, **kwargs)

   list_display = ('nazev', 'slug', 'aktivni', 'vyhledavani', 'zoom', 'uvodni_zprava',)
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

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
