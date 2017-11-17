# -*- coding: utf-8 -*-
import datetime

from django.contrib import sitemaps
try:
    from django.urls import reverse
except ImportError:  # Django<2.0
    from django.core.urlresolvers import reverse

from webmap.models import Poi


class PoiSitemap(sitemaps.Sitemap):
    def items(self):
        return Poi.visible.all()

    def changefreq(self, obj):
        return 'weekly'

    def lastmod(self, obj):
        return obj.last_modification

    def location(self, obj):
        return "%s#misto=%s_%s" % (reverse("mapa_view", kwargs={"poi_id": obj.pk}), obj.marker.layer.slug, obj.pk)


class NamesSitemap(sitemaps.Sitemap):
    def __init__(self, names):
        self.names = names

    def items(self):
        return self.names

    def changefreq(self, obj):
        return 'daily'

    def lastmod(self, obj):
        return datetime.datetime.now()

    def location(self, obj):
        return reverse(obj)
