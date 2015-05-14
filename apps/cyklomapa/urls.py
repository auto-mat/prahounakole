from django.conf import settings
from django.conf.urls import patterns, url, include
from django.contrib import admin

from cyklomapa.views import mapa_view, kml_view, popup_view, uzavirky_view, metro_view, znacky_view
from cyklomapa.feeds import UzavirkyFeed, NovinkyFeed
from httpproxy.views import HttpProxy
from django.contrib.comments.feeds import LatestCommentFeed

urlpatterns = patterns('',
    url(r'^$', mapa_view, name="mapa_view"),
    (r'^misto/(\d+)/$', mapa_view),
    url(r'^kml/([-\w]+)/$', kml_view, name="kml_view"),
    (r'^popup/(\d+)/$', popup_view),
    (r'^uzavirky/$', uzavirky_view),
    url(r'^uzavirky/feed/$', UzavirkyFeed(), name="uzavirky_feed"),
    url(r'^novinky/feed/$', NovinkyFeed(), name="novinky_feed"),
    (r'^metro/$', metro_view),
    (r'^znacky/$', znacky_view),
    url(r'^comments/', include('fluent_comments.urls')),
    url(r'^comments/feeds/latest/$', LatestCommentFeed(), name="latest_comments_feed"),
)

if settings.ENABLE_API_PROXY:
   urlpatterns += patterns('',
      (r'^(?P<url>api/.*)$', HttpProxy.as_view(base_url = settings.PROXY_BASE_URL)),
   )
