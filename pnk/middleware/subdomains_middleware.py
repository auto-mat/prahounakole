from django.conf import settings
from django.shortcuts import get_object_or_404
from cyklomapa.models import *
import re

class SubdomainsMiddleware:
    def process_request(self, request):
        request.domain = request.META['HTTP_HOST']
        request.subdomain = ''
        request.mobilni = False
        request.mesto = None
        parts = request.domain.split('.')

        if len(parts) == 3 or len(parts) == 4:
            request.subdomain = parts[0]
            request.domain = '.'.join(parts[1:])

            if 'm' in parts[0]:
                   request.mobilni = True
                   request.subdomain = parts[1]
                   request.domain = '.'.join(parts[2:])

            # najdeme mesto podle slugu. pokud neexistuje, vyhodime 404
            request.mesto = get_object_or_404(Mesto, slug = request.subdomain)
