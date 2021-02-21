from django.conf import settings
from django import template

register = template.Library()


@register.filter(name='get_file_path')
def get_file_path(value):
    """Get AWS S3 file path"""
    return value.split(settings.MEDIA_URL)[-1]
