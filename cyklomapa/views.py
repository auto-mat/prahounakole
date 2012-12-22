# views.py

import random, math
import urllib, re

from django.conf import settings
from django import forms, http
from django.shortcuts import render, render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.gis.shortcuts import render_to_kml
from django.views.decorators.cache import cache_page
from django.views.decorators.cache import never_cache
from django.views.decorators.gzip import *
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db.models import Q 

from cyklomapa.models import *

@gzip_page 
#@cache_page(24 * 60 * 60) # cachujeme view v memcached s platnosti 24h
def mapa_view(request, poi_id=None):
    vrstvy = Vrstva.objects.filter(status__show=True)
    # volitelne poi_id zadane mape jako bod, na ktery se ma zazoomovat
    center_poi = None
    if poi_id:
        try:
            center_poi = Poi.viditelne.get(id=poi_id)
        except Poi.DoesNotExist:
            pass

    if hasattr(settings, 'ROOT_URL'):
        ROOT_URL = settings.ROOT_URL
    else:
        ROOT_URL = '/'

    minimize_layerswitcher = request.GET.get('nols', 0)
    nomenu = request.GET.get('nomenu', 0)

    # detekce mobilni verze podle url
    subdomain = request.META.get('HTTP_HOST', '').split('.')
    mobilni = False
    if 'm' in subdomain:
        mobilni = True
        minimize_layerswitcher = 1
        nomenu = 1

    context = RequestContext(request, {
        'root_url': ROOT_URL,
        'vrstvy': vrstvy,
        'legenda': Legenda.objects.all(),
        'center_poi' : center_poi,
        'nomenu': nomenu,
        'minimize_layerswitcher': minimize_layerswitcher,
        'mobilni': mobilni,
    })
    return render_to_response('mapa.html', context_instance=context)

@gzip_page
@never_cache              # zabranime prohlizeci cachovat si kml
@cache_page(24 * 60 * 60) # cachujeme view v memcached s platnosti 24h
def kml_view(request, nazev_vrstvy):
    # najdeme vrstvu podle slugu. pokud neexistuje, vyhodime 404
    v = get_object_or_404(Vrstva, slug=nazev_vrstvy, status__show=True)

    # vsechny body co jsou v teto vrstve a jsou zapnute
    points = Poi.viditelne.filter(znacka__vrstva=v).kml()
    return render_to_kml("gis/kml/vrstva.kml", { 'places' : points})

@gzip_page
def popup_view(request, poi_id):
    poi = get_object_or_404(Poi, id=poi_id)

    return render(request, "gis/popup.html",
          context_instance=RequestContext(request, { 'poi' : poi }),
          content_type="application/xml")

# vyhledani poi podle nazvu nebo adresy
# v PNK se nepouziva
@gzip_page
def search_view(request, query):
    if len(query) < 3:
        return http.HttpResponseBadRequest('Insufficient query lenght')
    ikona = None

    #  nejdriv podle nazvu
    nazev_qs = Poi.viditelne.filter(Q(nazev__icontains=query))
    # pak podle popisu, adresy a nazvu znacky, pokud uz nejsou vyse
    extra_qs = Poi.viditelne.filter(Q(desc__icontains=query)|Q(address__icontains=query)|Q(znacka__nazev__icontains=query)).exclude(id__in=nazev_qs)
    # union qs nezachova poradi, tak je prevedeme na listy a spojime
    points = list(nazev_qs.kml()) + list(extra_qs.kml())
    return render_to_kml("gis/kml/vrstva.kml", {
        'places' : points,
        'ikona': ikona})

# vypisy uzavirek a metra pouzite na hlavnim webu PNK
@cache_page(24 * 60 * 60) # cachujeme view v memcached s platnosti 24h
def uzavirky_view(request):
    poi = Poi.objects.filter(status__show=True, znacka__slug='vyluka_akt')
    return render_to_response('uzavirky.html',
        context_instance=RequestContext(request, { 'uzavirky': poi }))

@cache_page(24 * 60 * 60) # cachujeme view v memcached s platnosti 24h
def metro_view(request):
    poi = Poi.objects.filter(status__show=True, znacka__slug__in=['metro_a', 'metro_b', 'metro_c']).order_by('znacka__slug', 'id')
    return render_to_response('metro.html',
        context_instance=RequestContext(request, { 'poi': poi }))

# View pro podrobny vypis vrstev
@cache_page(24 * 60 * 60) # cachujeme view v memcached s platnosti 24h
def znacky_view(request):
    vrstvy = Vrstva.objects.filter(status__show=True)
    znacky = Znacka.objects.filter(status__show=True)
    legenda = Legenda.objects.all()
    return render_to_response('znacky.html',
        context_instance=RequestContext(request, { 'vrstvy': vrstvy, 'znacky': znacky, 'legenda': legenda }))
