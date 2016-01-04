from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views

admin.autodiscover()


urlpatterns = (
    url(r'^admin/passreset/$', auth_views.password_reset, name='password_reset'),
    url(r'^admin/passresetdone/$', auth_views.password_reset_done, name='password_reset_done'),
    url(r'^admin/passresetconfirm/(?P<uidb64>[-\w]+)/(?P<token>[-\w]+)/$', auth_views.password_reset_confirm, name='password_reset_confirm'),
    url(r'^admin/passresetcomplete/$', auth_views.password_reset_complete, name='password_reset_complete'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin/', include("massadmin.urls")),
    url(r'^chaining/', include('smart_selects.urls')),
    url(r'^webmap/', include('webmap.urls')),
    url(r'^feedback/', include('feedback.urls')),
    url(r'^', include("cyklomapa.urls")),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
