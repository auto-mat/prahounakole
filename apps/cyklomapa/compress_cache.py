# -*- coding: utf-8 -*-

from compressor.signals import post_compress
from django.dispatch import receiver
from django.core.cache import cache

@receiver(post_compress)
def compress(sender, *args, **kwargs):
    context = kwargs['context']
    mode = kwargs['mode']
    if mode == 'file':
       cache.set("compressed_" + context['compressed']['name'], context['compressed']['url'])
