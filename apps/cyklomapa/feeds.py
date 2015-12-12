#coding=utf-8
from django.contrib.syndication.views import Feed

from webmap.models import Poi


class UzavirkyFeed(Feed):
        title = u"Prahou Na Kole - aktuální uzavírky"
        link = "/sitenews/"
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
        title = u"Prahou Na Kole - novinky v mapě"
        link = "/sitenews/"
        description = u"Novinky v mapě"

        def get_object(self, request):
                return request.mesto

        def items(self, obj):
                return Poi.objects.filter(status__name="active", geom__contained=obj.sektor.geom).order_by('last_modification').reverse()[:10]

        def item_pubdate(self, item):
                return item.last_modification

        def item_title(self, item):
                return str(item)

        def item_description(self, item):
                return item.desc
