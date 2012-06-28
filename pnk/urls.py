from django.conf import settings
from django.conf.urls import patterns, url, include
from django.conf.urls.static import static
from django.contrib import admin

from cyklomapa.views import *
from cyklomapa.feeds import UzavirkyFeed

admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', mapa_view),
    (r'^misto/(\d+)/$', mapa_view),
    (r'^kml/([-\w]+)/$', kml_view),
    (r'^popup/(\d+)/$', popup_view),
    (r'^uzavirky/$', uzavirky_view),
    (r'^uzavirky/feed/$', UzavirkyFeed()),
    (r'^metro/$', metro_view),
    (r'^admin/', include(admin.site.urls)),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
