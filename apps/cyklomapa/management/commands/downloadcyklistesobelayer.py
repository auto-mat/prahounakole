import json
import pathlib

from django.conf import settings
from django.core.management import BaseCommand

from cyklomapa.utils import parse_cykliste_sobe_features


class Command(BaseCommand):
    """Download cykliste sobe features JSON layer files"""
    help = "Download cykliste sobe features JSON layer files" # noqa

    def handle(self, *args, **options):
        features = parse_cykliste_sobe_features()
        with open(pathlib.Path(settings.STATIC_ROOT) / "list.json", "w") as f:
            json.dump(features, f)
