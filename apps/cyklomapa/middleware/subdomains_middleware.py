from django.conf import settings
from cyklomapa.models import Mesto


class SubdomainsMiddleware:
    def process_request(self, request):
        request.domain = request.META['HTTP_HOST']
        request.subdomain = ''
        request.mesto = None
        parts = request.domain.split('.')

        if len(parts) in (2, 3, 4):
            request.subdomain = parts[0]
            request.domain = '.'.join(parts[1:])
        else:
            # fallback na Prahu
            request.subdomain = 'mapa'

        # umoznime nastavit subdomenu pomoci settings
        request.subdomain = getattr(settings, 'FORCE_SUBDOMAIN', request.subdomain)

        # najdeme mesto podle slugu. pokud neexistuje, vyhodime 404
        try:
            request.mesto = Mesto.objects.get(sektor__slug=request.subdomain)
        except Mesto.DoesNotExist:
            request.mesto = None
