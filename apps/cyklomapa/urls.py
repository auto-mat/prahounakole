from cyklomapa.feeds import NovinkyFeed, UzavirkyFeed
from cyklomapa.views import (
    PanelHledaniView, PanelInformaceView,
    PanelMapaView, PopupListView, kml_view, mapa_view, metro_view,
    popup_view, uzavirky_view, znacky_view,
)

from django.conf import settings
from django.conf.urls import include, url
from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponse
from django.views.decorators.cache import cache_page
from django.views.generic.base import RedirectView

from django_comments.feeds import LatestCommentFeed

from httpproxy.views import HttpProxy

from .sitemap import NamesSitemap, PoiSitemap

sitemaps = {
    'pages': NamesSitemap(['mapa_view']),
    'pois': PoiSitemap(),
}

urlpatterns = [
    url(r'^$', mapa_view, name="mapa_view"),
    url(r'^misto/(?P<poi_id>\d+)/$', mapa_view, name="mapa_view"),
    url(r'^kml/([-\w]+)/$', kml_view, name="kml_view"),
    url(r'^popup/(\d+)/$', popup_view, name="popup_view"),
    url(r'^uzavirky/$', uzavirky_view, name="uzavirky_view"),
    url(r'^uzavirky/feed/$', UzavirkyFeed(), name="uzavirky_feed"),
    url(r'^novinky/feed/$', NovinkyFeed(), name="novinky_feed"),
    url(r'^metro/$', metro_view, name="metro_view"),
    url(r'^znacky/$', znacky_view, name="znacky_view"),
    url(r'^panel-mapa/$', PanelMapaView.as_view(), name="panel_mapa_view"),
    url(r'^panel-informace/$', PanelInformaceView.as_view(), name="panel_informace_view"),
    url(r'^panel-hledani/$', PanelHledaniView.as_view(), name="panel_hledani_view"),
    url(r'^popup-list/$', PopupListView.as_view(), name="popup-list"),
    url(r'^comments/', include('fluent_comments.urls')),
    url(r'^comments/feeds/latest/$', LatestCommentFeed(), name="latest_comments_feed"),
    url(r'^robots.txt$', lambda r: HttpResponse("User-agent: *\nDisallow: /popup-list\nDisallow: /popup/*\nUser-agent: LinkChecker\nAllow:", content_type="text/plain")),
    url(r'^sitemap\.xml$', cache_page(24 * 60 * 60)(sitemap), {'sitemaps': sitemaps}, name='sitemap'),

    # Redirect from most frequent error links
    url(r'^jak-na-to$', RedirectView.as_view(url='http://prahounakole.cz/jak-do-mesta/deset-zasad-jak-zacit/', permanent=True)),
]

if settings.ENABLE_API_PROXY:
    urlpatterns += [
        url(r'^(?P<url>api/.*)$', HttpProxy.as_view(base_url=settings.PROXY_BASE_URL)),
    ]
