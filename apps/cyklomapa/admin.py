# -*- coding: utf-8 -*-
# admin.py

# This file controls the look and feel of the models within the Admin App
# They appear in the admin app once they are registered at the bottom of
# this code (same goes for the databrowse app)

from django.conf import settings  # needed if we use the GOOGLE_MAPS_API_KEY from settings

# Import the admin site reference from django.contrib.admin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

# Grab the Admin Manager that automaticall initializes an OpenLayers map
# for any geometry field using the in Google Mercator projection with OpenStreetMap basedata
from django.contrib.gis.admin import OSMGeoAdmin
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models import Union

from cyklomapa.models import UserMesto, Upresneni, Mesto, MarkerZnacka
from webmap.models import Marker, Poi
from webmap.admin import MarkerAdmin, PoiAdmin

USE_GOOGLE_TERRAIN_TILES = False


# Define an inline admin descriptor for Employee model
# which acts a bit like a singleton
class UserMestoInline(admin.StackedInline):
    filter_horizontal = ('mesta',)
    model = UserMesto
    can_delete = False
    verbose_name_plural = 'Uzivatelska mesta'


# Define a new User admin
class UserAdmin(UserAdmin):
    list_display = ('__unicode__', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'is_active', 'last_login', 'get_groups', 'get_user_permissions', 'usermesto__mesta')
    inlines = (UserMestoInline, )

    def get_groups(self, obj):
        if obj:
            return ", ".join([group.name for group in obj.groups.all()])

    def get_user_permissions(self, obj):
        if obj:
            return ", ".join([user_permission.name for user_permission in obj.user_permissions.all()])

    def usermesto__mesta(self, obj):
        if obj:
            return ", ".join([mesto.sektor.name for mesto in obj.usermesto.mesta.all()])


class MestoPoiAdmin(PoiAdmin):
    def queryset(self, request):
        queryset = super(MestoPoiAdmin, self).queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(geom__intersects=request.user.usermesto.mesta.aggregate(Union('sektor__geom'))['sektor__geom__union'])

    def get_form(self, request, obj=None, **kwargs):
        mesto = Mesto.objects.get(sektor__slug=request.subdomain)
        pnt = Point(mesto.geom.x, mesto.geom.y, srid=4326)
        pnt.transform(900913)
        self.default_lon, self.default_lat = pnt.coords

        form = super(MestoPoiAdmin, self).get_form(request, obj, **kwargs)
        return form

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "mesto":
            if request.user.is_superuser:
                kwargs["queryset"] = Mesto.objects
            else:
                kwargs["queryset"] = request.user.usermesto.mesta.all()

        return super(MestoPoiAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


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


class MestoInline(admin.StackedInline):
    model = Mesto
    can_delete = False
    verbose_name_plural = 'Parametry města'


#TODO: make Mesto map to display OSM
#class MestoSectorAdmin(SectorAdmin):
#    inlines = SectorAdmin.inlines + [MestoInline,]


class MarkerZnackaInline(admin.StackedInline):
    model = MarkerZnacka
    can_delete = False
    verbose_name_plural = 'Parametry značky'


class MarkerZnackaAdmin(MarkerAdmin):
    inlines = MarkerAdmin.inlines + [MarkerZnackaInline, ]


class MestoAdmin(OSMGeoAdmin):
    list_display = ('sektor', 'zoom', 'aktivni', 'vyhledavani', 'uvodni_zprava', )

    def queryset(self, request):
        queryset = super(MestoAdmin, self).queryset(request)
        if request.user.is_superuser:
            return queryset

        return queryset.filter(id__in=request.user.usermesto.mesta.all())

    def get_form(self, request, obj=None, **kwargs):
        if not request.user.has_perm(u"cyklomapa.can_edit_all_fields"):
            self.readonly_fields = ('vyhledavani', 'aktivni', 'sektor')
        return super(MestoAdmin, self).get_form(request, obj=None, **kwargs)

    if USE_GOOGLE_TERRAIN_TILES:
        map_template = 'gis/admin/google.html'
        extra_js = ['http://openstreetmap.org/openlayers/OpenStreetMap.js', 'http://maps.google.com/maps?file=api&amp;v=2&amp;key=%s' % settings.GOOGLE_MAPS_API_KEY]
    else:
        pass  # defaults to OSMGeoAdmin presets of OpenStreetMap tiles

    default_lon = 1605350
    default_lat = 6461466
    default_zoom = 12
    scrollable = True
    map_width = 700
    map_height = 500
    map_srid = 900913


admin.site.unregister(User)
admin.site.register(User, UserAdmin)

#admin.site.unregister(Sector)
#admin.site.register(Sector, MestoSectorAdmin)

admin.site.register(Mesto, MestoAdmin)

admin.site.unregister(Marker)
admin.site.register(Marker, MarkerZnackaAdmin)

admin.site.unregister(Poi)
admin.site.register(Poi, MestoPoiAdmin)
