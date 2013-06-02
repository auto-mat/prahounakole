#coding=utf-8
from django.contrib.syndication.views import Feed
from cyklomapa.models import Poi

class UzavirkyFeed(Feed):
        title = u"Prahou Na Kole - aktuální uzavírky"
        link = "/sitenews/"
        description = u"Aktuální uzavírky cyklostezek a cyklotras"

        def get_object(self, request):
                return request.mesto

        def items(self, obj):
                return Poi.objects.filter(mesto=obj, status__show=True, znacka__slug='vyluka_akt')

        def item_title(self, item):
                return unicode(item)

        def item_description(self, item):
                return item.desc 

class NovinkyFeed(Feed):
        title = u"Prahou Na Kole - novinky v mapě"
        link = "/sitenews/"
        description = u"Novinky v mapě"

        def get_object(self, request):
                return request.mesto

        def items(self, obj):
                return Poi.objects.filter(status=4, mesto=obj).order_by('datum_zmeny').reverse()[:10]

        def item_title(self, item):
                return unicode(item)

        def item_description(self, item):
                return item.desc
