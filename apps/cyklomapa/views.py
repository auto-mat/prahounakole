# views.py

import random, math
import urllib, re

from django.conf import settings
from django import forms, http
from django.shortcuts import render, render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.gis.shortcuts import render_to_kml
from django.views.decorators.cache import cache_page
from django.core.cache import get_cache
from django.views.decorators.cache import never_cache
from django.views.decorators.gzip import *
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db.models import Q 
from django.contrib.sites.models import get_current_site


from webmap.models import OverlayLayer, Marker, Poi, Legend

# kopie  django.contrib.admin.views.main.get_query_string
from django.utils.http import urlencode
def get_query_string(params, new_params=None, remove=None):
    if new_params is None: new_params = {}
    if remove is None: remove = []
    p = params.copy()
    for r in remove:
        for k in p.keys():
            if k.startswith(r):
                del p[k]
    for k, v in new_params.items():
        if v is None:
            if k in p:
                del p[k]
        else:
            p[k] = v
    return '?%s' % urlencode(p)

@gzip_page 
#@cache_page(24 * 60 * 60) # cachujeme view v memcached s platnosti 24h
def mapa_view(request, poi_id=None):

    # hack pro kompatibilitu se starsimu url po pridani vrstvy rekola
    layers = request.GET.get('layers', None)
    if layers:
        if len(layers) == 14:
            newlayers = layers[0:13] + 'F' + layers[13]
            params = get_query_string(dict(request.GET.items()), { 'layers' : newlayers })
            return http.HttpResponseRedirect(request.path + params)

    vrstvy = OverlayLayer.objects.filter(status__show=True)
    # volitelne poi_id zadane mape jako bod, na ktery se ma zazoomovat
    center_poi = None
    if poi_id:
        try:
            center_poi = Poi.visible.get(id=poi_id)
        except Poi.DoesNotExist:
            pass

    if hasattr(settings, 'ROOT_URL'):
        ROOT_URL = settings.ROOT_URL
    else:
        ROOT_URL = ''

    minimize_layerswitcher = request.GET.get('nols', 0)
    nomenu = request.GET.get('nomenu', 0)

    # detekce mobilni verze podle url
    if request.mobilni:
        minimize_layerswitcher = 1
        nomenu = 1

    historie = Poi.objects.filter(status__show=True, geom__intersects=request.mesto.sektor.geom).order_by('last_modification').reverse()[:10]

    context = RequestContext(request, {
        'root_url': ROOT_URL,
        'vrstvy': vrstvy,
        'legenda': Legend.objects.all(),
        'center_poi' : center_poi,
        'nomenu': nomenu,
        'mesto': request.mesto,
        'minimize_layerswitcher': minimize_layerswitcher,
        'mobilni': request.mobilni,
        'historie': historie
    })
    if not request.mesto.aktivni and not request.user.is_authenticated():
       return render_to_response('neaktivni.html', context_instance=context)

    return render_to_response('mapa.html', context_instance=context)

def cache_page_mesto(expiration):
   def cache_page_mesto_dc(fn):
       def wrapper(*args, **kwargs):
          cache = get_cache('default')

          cache_key = 'kml_view_' + args[1] + '_' + args[0].mesto.sektor.slug
          result = cache.get(cache_key)
          if result == None:
             result = fn(*args, **kwargs)
             cache.set( cache_key, result, expiration ) 
          return result
       return wrapper
   return cache_page_mesto_dc

@gzip_page
@never_cache              # zabranime prohlizeci cachovat si kml
@cache_page_mesto(24 * 60 * 60) # cachujeme view v memcached s platnosti 24h
def kml_view(request, nazev_vrstvy):
    # najdeme vrstvu podle slugu. pokud neexistuje, vyhodime 404
    v = get_object_or_404(OverlayLayer, slug=nazev_vrstvy, status__show=True)

    # vsechny body co jsou v teto vrstve a jsou zapnute
    points = Poi.visible.filter(marker__layer=v).filter(geom__intersects = request.mesto.sektor.geom).kml()
    return render_to_kml("webmap/gis/kml/layer.kml", {
       'places' : points,
       'site': get_current_site(request).domain,
    })

@gzip_page
def popup_view(request, poi_id):
    poi = get_object_or_404(Poi, id=poi_id)

    return render(request, "gis/popup.html",
          context_instance=RequestContext(request, {
              'poi' : poi,
              'fotky': poi.photos.all(),
              'settings': settings,
              'can_change': request.user.has_perm('webmap.change_poi')# and poi.has_change_permission(request.user),
              }),
          content_type="application/xml")

# vyhledani poi podle nazvu nebo adresy
# v PNK se nepouziva
@gzip_page
def search_view(request, query):
    if len(query) < 3:
        return http.HttpResponseBadRequest('Insufficient query lenght')
    ikona = None

    #  nejdriv podle nazvu
    nazev_qs = Poi.visible.filter(Q(name__icontains=query))
    # pak podle popisu, adresy a nazvu znacky, pokud uz nejsou vyse
    extra_qs = Poi.visible.filter(Q(desc__icontains=query)|Q(address__icontains=query)|Q(marker__name__icontains=query)).exclude(id__in=nazev_qs)
    # union qs nezachova poradi, tak je prevedeme na listy a spojime
    points = list(nazev_qs.kml()) + list(extra_qs.kml())
    return render_to_kml("gis/kml/vrstva.kml", {
        'places' : points,
        'ikona': ikona})

# vypisy uzavirek a metra pouzite na hlavnim webu PNK
@cache_page(24 * 60 * 60) # cachujeme view v memcached s platnosti 24h
def uzavirky_view(request):
    poi = Poi.objects.select_related('marker').filter(status__show=True, marker__slug='vyluka_akt')
    return render_to_response('uzavirky.html',
        context_instance=RequestContext(request, { 'uzavirky': poi }))

@cache_page(24 * 60 * 60) # cachujeme view v memcached s platnosti 24h
def metro_view(request):
    poi = Poi.objects.select_related('marker').filter(status__show=True, marker__slug__in=['metro_a', 'metro_b', 'metro_c']).order_by('marker__slug', 'id')
    return render_to_response('metro.html',
        context_instance=RequestContext(request, { 'poi': poi }))

# View pro podrobny vypis vrstev
@cache_page(24 * 60 * 60) # cachujeme view v memcached s platnosti 24h
def znacky_view(request):
    vrstvy = OverlayLayer.objects.filter(status__show=True)
    znacky = Marker.objects.select_related('layer').filter(status__show=True)
    legenda = Legend.objects.all()
    return render_to_response('znacky.html',
        context_instance=RequestContext(request, { 'vrstvy': vrstvy, 'znacky': znacky, 'legenda': legenda }))
