import pathlib
import subprocess
import tempfile

from django.conf import settings
from django.contrib.gis.geos import GeometryCollection, LineString
from django.contrib.gis.utils import LayerMapping
from django.core.management import BaseCommand, CommandError
from django.db import connection
from django.utils.translation import gettext as _

from webmap.models import  Marker, OverlayLayer, Poi

from cyklomapa.models import CzechiaRegions, czechiaregions_mapping


class Command(BaseCommand):
    """Load/update geodata"""
    help = 'Load/update geodata' # noqa

    def _import_geodata(self, model, model_mapping, geodata_path):
        """Import geodata into model

        :param model obj: model object
        :param model_mapping dict: model fields mapping
        :param geodata_path str: geodata layer path
        """
        lm = LayerMapping(model=model, data=str(geodata_path),
                          mapping=model_mapping, transform=False)
        lm.save(strict=True, verbose=False)

    def _import_geodata_grom_ruian_db(
            self, layer, output_filename, temp_dir,
    ):
        """Import geodata layer from RUIAN DB

        :param layer str: name of RUIAN DB geodata layer
        :param output_filename str: output geodata filename
        :param temp_dir str: temp dir path

        :return geodata str: geodata layer path (exported from RUIAN DB)
        """

        geodata = (pathlib.Path(temp_dir) / "gdal-vfr" /
                   "data" / output_filename)

        import_geodata = (pathlib.Path(__file__).parent.absolute() /
                          "import_geodata_from_ruian_db.sh")
        p = subprocess.Popen(
            [import_geodata, layer, output_filename, temp_dir],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()

        if p.returncode != 0:
            if stderr:
                raise CommandError(
                    _("Error executing command '%(script)s'\n"
                      "'%(error)s'") % {
                          "script": import_geodata,
                          "error": stderr.decode('utf-8'),
                      }
                )

        return geodata

    def _import_cz_regions(self, temp_dir):
        """Import Czechia regions (Kraje) geodata layer from RUIAN DB

        :param temp_dir str: temp dir path
        """
        filename = "cz_regions.db"
        layer = "Vusc"  # kraje

        CzechiaRegions.objects.all().delete()
        with connection.cursor() as cursor:
            q = f"TRUNCATE {CzechiaRegions._meta.db_table} RESTART IDENTITY"
            cursor.execute(q)

        regions_geodata_path = self._import_geodata_grom_ruian_db(
            layer=layer, output_filename=filename, temp_dir=temp_dir,
        )

        self._import_geodata(
            model=CzechiaRegions, model_mapping=czechiaregions_mapping,
            geodata_path=regions_geodata_path,
        )
        self.stdout.write(_("'%(model)s' model(s) created.") % {
            "model": CzechiaRegions.__name__}
        )


        # Create Poi regions (line geom type representation)
        overlay, created = OverlayLayer.objects.get_or_create(
            name="Kraj", desc="CZ Kraje",
        )
        marker, created = Marker.objects.get_or_create(
            name="Kraj", desc="CZ Kraje", line_width=5.0,
            line_color="#ff0000", layer=overlay
        )

        objs = []
        count = 0
        for r in CzechiaRegions.objects.all():
            p, created = Poi.objects.get_or_create(
                name=r.nazev, marker=marker,
                geom=GeometryCollection(
                    LineString(r.geom.boundary.coords[0]),
                ),
            )
            count += 1
            if not created:
                p.geom = GeometryCollection(
                    LineString(r.geom.boundary.coords[0]),
                )
                objs.append(p)

        message = _("%(feat)s of 'Poi' models (represented Czechia regions - "
                    " Kraje) with line geometry type") % {
                        "feat": len(objs) if objs else count}

        if objs:
            CzechiaRegions.objects.bulk_update(objs, ["geom"])
            self.stdout.write(_("%(message)s was %(action)s.") % {
                "message": message,
                "action": "updated"}
            )
        else:
            self.stdout.write(_("%(message)s was %(action)s.") % {
                "message": message,
                "action": "created"}
            )

    def add_arguments(self, parser):
        parser.add_argument(
            "--geodata",
            dest="geodata",
            choices=("cz_regions",),
            help=_("Choose geodata for import"),
        )

    def handle(self, *args, **options):
        cz_regions = options.get("geodata")

        with tempfile.TemporaryDirectory() as temp_dir:
            # CZ Regions (Kraje)
            if cz_regions:
                self.stdout.write(
                    _("Try import '%(layer)s' geodata layer.") %
                    {"layer": cz_regions}
                )
                self._import_cz_regions(temp_dir=temp_dir)
                self.stdout.write(
                    self.style.SUCCESS(
                        _("Import of geodata layer '%(layer)s' was"
                          " successful.") % {"layer": cz_regions}
                    ),
                )
