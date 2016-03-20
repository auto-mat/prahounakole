# -*- coding: utf-8 -*-
# admin.py

# This file controls the look and feel of the models within the Admin App
# They appear in the admin app once they are registered at the bottom of
# this code (same goes for the databrowse app)

# Import the admin site reference from django.contrib.admin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from leaflet.admin import LeafletGeoAdmin, LeafletGeoAdminMixin
from django.contrib.gis.db.models import Union

from cyklomapa.models import MarkerZnacka, Mesto, Upresneni, UserMesto
from webmap.admin import MarkerAdmin, PoiAdmin, SectorAdmin
from webmap.models import Marker, Poi, Sector

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
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'is_active', 'last_login', 'get_groups', 'get_user_permissions', 'usermesto__mesta')
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
    def get_queryset(self, request):
        queryset = super(MestoPoiAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(geom__intersects=request.user.usermesto.mesta.aggregate(Union('sektor__geom'))['sektor__geom__union'])

    def get_form(self, request, obj=None, **kwargs):
        form = super(MestoPoiAdmin, self).get_form(request, obj, **kwargs)
        mesto = Mesto.objects.get(sektor__slug=request.subdomain)
        self.settings_overrides = {
            'DEFAULT_CENTER': (mesto.geom.y, mesto.geom.x),
            'DEFAULT_ZOOM': 12,
        }
        return form

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "mesto":
            if request.user.is_superuser:
                kwargs["queryset"] = Mesto.objects
            else:
                kwargs["queryset"] = request.user.usermesto.mesta.all()

        return super(MestoPoiAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def __init__(self, *args, **kwargs):
        super(MestoPoiAdmin, self).__init__(*args, **kwargs)
        self.list_filter += ("photos__license",)


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


class MestoInline(LeafletGeoAdminMixin, admin.StackedInline):
    model = Mesto
    can_delete = False
    verbose_name_plural = 'Parametry města'


class MestoSectorAdmin(SectorAdmin):
    inlines = SectorAdmin.inlines + [MestoInline, ]


class MarkerZnackaInline(admin.StackedInline):
    model = MarkerZnacka
    can_delete = False
    verbose_name_plural = 'Parametry značky'


class MarkerZnackaAdmin(MarkerAdmin):
    inlines = MarkerAdmin.inlines + [MarkerZnackaInline, ]


class MestoAdmin(LeafletGeoAdmin):
    list_display = ('sektor', 'zoom', 'aktivni', 'vyhledavani', 'uvodni_zprava', )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset

        return queryset.filter(id__in=request.user.usermesto.mesta.all())

    def get_form(self, request, obj=None, **kwargs):
        if not request.user.has_perm(u"cyklomapa.can_edit_all_fields"):
            self.readonly_fields = ('vyhledavani', 'aktivni', 'sektor')
        return super(MestoAdmin, self).get_form(request, obj=None, **kwargs)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.unregister(Sector)
admin.site.register(Sector, MestoSectorAdmin)

admin.site.register(Mesto, MestoAdmin)

admin.site.unregister(Marker)
admin.site.register(Marker, MarkerZnackaAdmin)

admin.site.unregister(Poi)
admin.site.register(Poi, MestoPoiAdmin)
