import pathlib
import subprocess

from django.conf import settings
from django.contrib.gis.utils import LayerMapping
from django.core.management import BaseCommand, CommandError
from django.db import connection

from cyklomapa.models import CzechiaRegions, czechiaregions_mapping


class Command(BaseCommand):
    """Load/update geodata"""
    help = 'Load/update geodata' # noqa

    def handle(self, *args, **options):
        filename = "cz_regions_EPSG_4326.db"
        update_geodata = pathlib.Path(settings.BASE_DIR) / "load_geodata.sh"

        CzechiaRegions.objects.all().delete()
        with connection.cursor() as cursor:
            q = f"TRUNCATE {CzechiaRegions._meta.db_table} RESTART IDENTITY"
            cursor.execute(q)

        czechia_regions = (pathlib.Path(settings.BASE_DIR) / "gdal-vfr" /
                           "data" / filename)

        p = subprocess.Popen([update_geodata, filename],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()

        if p.returncode != 0:
            if stderr:
                raise CommandError(
                    f"Error executing command '{update_geodata}'\n"
                    f"{stderr.decode('utf-8')}",
                )

        lm = LayerMapping(CzechiaRegions, str(czechia_regions),
                          czechiaregions_mapping, transform=False)
        lm.save(strict=True, verbose=True)
