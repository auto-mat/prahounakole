import json
import pathlib

from django.conf import settings
from django.core.management import BaseCommand

from cyklomapa.utils import parse_cykliste_sobe_features
from cyklomapa.views import get_cyklisty_sobe_layer

class Command(BaseCommand):
    """Download cykliste sobe features JSON layer files"""
    help = "Download cykliste sobe features JSON layer files" # noqa

    def handle(self, *args, **options):
        parse_cykliste_sobe_features(
            save_to_file=get_cyklisty_sobe_layer.features_file_path,
        )
