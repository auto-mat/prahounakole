# -*- coding: utf-8 -*-

from compressor.management.commands.compress import Command as OldCommand
import os

from compressor.signals import post_compress
from django.dispatch import receiver


def normpath(*args):
    return os.path.normpath(os.path.abspath(os.path.join(*args)))
file_name = normpath(__file__, "..", "..", "..", "templates", 'compress_cache_manifest.txt')


@receiver(post_compress)
def compress(sender, *args, **kwargs):
    context = kwargs['context']
    mode = kwargs['mode']
    if mode == 'file':
        with open(file_name, "a") as manifest_file:
            manifest_file.write(context['compressed']['url'] + "\n")


class Command(OldCommand):
    def compress(self, *args, **kwargs):
        try:
            os.remove(file_name)
        except OSError:
            pass
        return super(Command, self).compress(*args, **kwargs)
