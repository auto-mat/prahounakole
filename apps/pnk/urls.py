from django.conf import settings
from django.conf.urls import patterns, url, include
from django.contrib import admin

from cyklomapa.views import *
from cyklomapa.feeds import UzavirkyFeed

urlpatterns = patterns('',
    (r'^$', mapa_view),
    (r'^misto/(\d+)/$', mapa_view),
    (r'^kml/([-\w]+)/$', kml_view),
    (r'^popup/(\d+)/$', popup_view),
    (r'^uzavirky/$', uzavirky_view),
    (r'^uzavirky/feed/$', UzavirkyFeed()),
    (r'^metro/$', metro_view),
    (r'^znacky/$', znacky_view),
)

if settings.ENABLE_API_PROXY:
   urlpatterns += patterns('',
      (r'^(?P<url>api/.*)$', 'httpproxy.views.proxy'),
   )
