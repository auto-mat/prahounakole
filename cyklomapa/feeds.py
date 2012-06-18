#coding=utf-8
from django.contrib.syndication.views import Feed
from cyklomapa.models import Poi

class UzavirkyFeed(Feed):
        title = u"Prahou Na Kole - aktuální uzavírky"
        link = "/sitenews/"
        description = u"Aktuální uzavírky pražských cyklostezek a cyklotras"

        def items(self):
                return Poi.objects.filter(status__show=True, znacka__slug='vyluka_akt')

        def item_title(self, item):
                return unicode(item)

        def item_description(self, item):
                return item.desc 
