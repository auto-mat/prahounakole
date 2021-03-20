# -*- coding: utf-8 -*-
from django.contrib.syndication.views import Feed

from .models import Poi


class UzavirkyFeed(Feed):
    title = "Městem na kole - aktuální uzavírky"
    link = "/"
    description = u"Aktuální uzavírky cyklostezek a cyklotras"

    def get_object(self, request):
        return request.mesto

    def items(self, obj):
        return Poi.objects.filter(geom__contained=obj.sektor.geom, status__show=True, marker__slug='vyluka_akt')

    def item_pubdate(self, item):
        return item.last_modification

    def item_title(self, item):
        return str(item)

    def item_description(self, item):
        return item.desc


class NovinkyFeed(Feed):
    title = "Městem na kole - novinky v mapě"
    link = "/"
    description = u"Novinky v mapě"

    def get_object(self, request):
        return request.mesto

    def items(self, obj):
        return Poi.objects.filter(status__show=True, geom__contained=obj.sektor.geom).order_by('last_modification').reverse()[:10]

    def item_pubdate(self, item):
        return item.last_modification

    def item_title(self, item):
        return str(item)

    def item_description(self, item):
        return item.desc
