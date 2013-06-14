from django.conf import settings
from django.conf.urls import patterns, url, include
from django.contrib import admin

from cyklomapa.views import *
from cyklomapa.feeds import UzavirkyFeed, NovinkyFeed
from httpproxy.views import HttpProxy

urlpatterns = patterns('',
    (r'^$', mapa_view),
    (r'^misto/(\d+)/$', mapa_view),
    (r'^kml/([-\w]+)/$', kml_view),
    (r'^popup/(\d+)/$', popup_view),
    (r'^uzavirky/$', uzavirky_view),
    url(r'^uzavirky/feed/$', UzavirkyFeed(), name="uzavirky_feed"),
    url(r'^novinky/feed/$', NovinkyFeed(), name="novinky_feed"),
    (r'^metro/$', metro_view),
    (r'^znacky/$', znacky_view),
)

if settings.ENABLE_API_PROXY:
   urlpatterns += patterns('',
      (r'^(?P<url>api/.*)$', HttpProxy.as_view(base_url = settings.PROXY_BASE_URL)),
   )
