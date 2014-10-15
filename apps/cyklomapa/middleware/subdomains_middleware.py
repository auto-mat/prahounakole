from django.conf import settings
from django.shortcuts import get_object_or_404
from cyklomapa.models import Mesto
import re

class SubdomainsMiddleware:
    def process_request(self, request):
        request.domain = request.META['HTTP_HOST']
        request.subdomain = ''
        request.mobilni = False
        request.mesto = None
        parts = request.domain.split('.')

        if len(parts) in (2, 3, 4):
            request.subdomain = parts[0]
            request.domain = '.'.join(parts[1:])

            if 'm' == parts[0]:
                   request.mobilni = True
                   request.subdomain = parts[1]
                   request.domain = '.'.join(parts[2:])
        else:
            # fallback na Prahu
            request.subdomain = 'mapa'

        # umoznime nastavit subdomenu pomoci settings
        request.subdomain = getattr(settings, 'FORCE_SUBDOMAIN', request.subdomain)

        # najdeme mesto podle slugu. pokud neexistuje, vyhodime 404
        request.mesto = get_object_or_404(Mesto, sektor__slug = request.subdomain)
