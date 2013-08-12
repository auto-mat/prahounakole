from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf.urls.static import static
admin.autodiscover()

from django.conf import settings

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin/', include("massadmin.urls")),
    url(r'^chaining/', include('smart_selects.urls')),
    url(r'^', include("cyklomapa.urls")),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
