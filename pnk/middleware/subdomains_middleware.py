from django.conf import settings
import re

class SubdomainsMiddleware:
    def process_request(self, request):
        request.domain = request.META['HTTP_HOST']
        request.subdomain = ''
        parts = request.domain.split('.')

        if len(parts) == 3:
            request.subdomain = parts[0]
            request.domain = '.'.join(parts[1:])
