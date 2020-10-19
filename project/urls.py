from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views

admin.autodiscover()


urlpatterns = [
    url(r'^admin/passreset/$', auth_views.PasswordResetView.as_view(), name='password_reset'),
    url(r'^admin/passresetdone/$', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    url(r'^admin/passresetconfirm/(?P<uidb64>[-\w]+)/(?P<token>[-\w]+)/$', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    url(r'^admin/passresetcomplete/$', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    url(r'^admin/', admin.site.urls),
    url(r'^admin/', include("massadmin.urls")),
    url(r'^webmap/', include('webmap.urls')),
    url(r'^feedback/', include('feedback.urls')),
    url(r'^', include("cyklomapa.urls")),
    url(r'^captcha/', include('captcha.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
