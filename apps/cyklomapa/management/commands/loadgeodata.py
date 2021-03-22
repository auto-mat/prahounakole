#!/usr/bin/env python

import pathlib
import subprocess
import tempfile

from django.conf import settings
from django.contrib.gis.geos import GeometryCollection, LineString
from django.contrib.gis.utils import LayerMapping
from django.core.management import BaseCommand, CommandError
from django.db import connection
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext as _

from webmap.models import Marker, OverlayLayer, Poi

from cyklomapa.models import (
    CzechiaAccidents, czechiaaccidents_mapping,
    CzechiaRegions, czechiaregions_mapping,
)


class Command(BaseCommand):
    """Load/update geodata"""
    help = 'Load/update geodata' # noqa

    start_date_message = _("Start-Date: %(datetime)s") # noqa
    end_date_message = _("End-Date: %(datetime)s") # noqa
    datetime_format = "%d-%m-%Y  %H:%M" # noqa

    def _import_geodata(self, model, model_mapping, geodata_path,
                        unique=None):
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
        name = "Kraj"
        desc = "CZ Kraje"
        order = max(OverlayLayer.objects.all().values_list(
            "order", flat=True)) + 1
        overlay, created = OverlayLayer.objects.get_or_create(
            name=name, desc=desc, slug="kraje", enabled=False,
        )
        if created:
            overlay.order = order
            overlay.minzoom = 14
            overlay.maxzoom = 10
            overlay.save()
        marker, created = Marker.objects.get_or_create(
            name=name, desc=desc, line_width=5.0,
            line_color="#ff0000", layer=overlay, slug="kraj",
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
            self.stdout.write(_("%(message)s has been %(action)s.") % {
                "message": message,
                "action": "updated"}
            )
        else:
            self.stdout.write(_("%(message)s has been %(action)s.") % {
                "message": message,
                "action": "created"}
            )

    def _create_cz_accidents_poi(self, query):
        """Create Czechia accidents Poi models

        :param dict query: CzechiaAccidents model query
        """
        name = "Nehody (srážka s jízdním kolem)"
        desc = "CZ Nehody (srážka s jízdním kolem)"
        order = max(OverlayLayer.objects.all().values_list(
            "order", flat=True)) + 1
        overlay, created = OverlayLayer.objects.get_or_create(
            name=name, desc=desc, slug="nehody", enabled=False,
        )
        if created:
            overlay.order = order
            overlay.save()
        marker, created = Marker.objects.get_or_create(
            name=name, desc=desc, default_icon="ikony/accident.png",
            layer=overlay, slug="nehoda",
        )

        objs = []
        null = "neznámý"
        for a in CzechiaAccidents.objects.filter(
                Q(zavineni="řidičem motorového vozidla",
                  vozidlo="jízdní kolo") |
                Q(zavineni="řidičem nemotorového vozidla",
                  vozidlo="jízdní kolo"), **query):
            desc = (f"dátum: {a.datum if a.datum else null}<br/>"
                    f"den: {a.den if a.den else null}<br/>"
                    f"čas: {a.cas if a.cas else null}<br/>"
                    f"následky: {a.nasledky if a.nasledky else null}<br/>"
                    f"zavinění: {a.zavineni if a.zavineni else null}<br/>"
                    f"vozidlo: {a.vozidlo if a.vozidlo else null}<br/>")

            objs.append(
                Poi(
                    name="Nehoda (srážka s jízdním kolem)",
                    marker=marker, desc=desc,
                    geom=GeometryCollection(a.geom),
                ),
            )
        Poi.objects.bulk_create(objs)
        message = _("%(feat)s of 'Poi' models (represented Czechia"
                    " accidents) with point geometry type") % {
                        "feat": len(objs)}

        self.stdout.write(_("%(message)s has been %(action)s.") % {
            "message": message,
            "action": "created"}
        )

    def _import_cz_accidents(self, temp_dir,
                             actual_previous_month_only=False):
        """Import/update Czechia accidents geodata

        https://www.policie.cz/clanek/statistika-nehodovosti-900835.aspx

        :param str temp_dir: temporary directory path
        :param bool actual_previous_month_only: if True only data from
        actual previous month will be downloaded
        """
        from .import_geodata.import_cz_accidents_geodata import (
            get_accident_data,
        )

        accidents_count = None
        query = {}

        if not actual_previous_month_only:
            CzechiaAccidents.objects.all().delete()
            with connection.cursor() as cursor:
                q = f"TRUNCATE {CzechiaAccidents._meta.db_table} RESTART IDENTITY"
                cursor.execute(q)
        else:
            accidents_count = CzechiaAccidents.objects.count()
            if accidents_count == 0:
                return
            # Actual previous month data only
            query = {
                "id__gt": CzechiaAccidents.objects.last().id
            }
            if not CzechiaAccidents.objects.filter(**query):
                self.stdout.write(_("No '%(model)s' model(s) has been"
                                    " created.") % {
                                        "model": CzechiaAccidents.__name__})
                return

        output_geodata = pathlib.Path(temp_dir) / "result.db"

        get_accident_data(
            output_csv_file=pathlib.Path(temp_dir) / "result.csv",
            output_sqlite_db_file=output_geodata,
            temp_dir=temp_dir,
            actual_previous_month_only=actual_previous_month_only,
        )
        if not output_geodata.exists():
            self.stdout.write(_("No '%(model)s' model(s) has been"
                                " created.") % {
                                    "model": CzechiaAccidents.__name__})
            return

        self._import_geodata(
            model=CzechiaAccidents,
            model_mapping=czechiaaccidents_mapping,
            geodata_path=output_geodata,
        )

        # Remove duplicates
        if accidents_count:
            fields = [f.name for f in CzechiaAccidents._meta.fields if
                      f.name not in ("id",)]
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    DELETE FROM {CzechiaAccidents._meta.db_table}
                    WHERE id IN (
                        SELECT
                            id
                        FROM (
                            SELECT
                                id,
                                row_number() OVER w as rnum
                            FROM {CzechiaAccidents._meta.db_table}
                            WINDOW w AS (
                                PARTITION BY {", ".join(fields)}
                                ORDER BY id
                            )

                        ) t
                    WHERE t.rnum > 1)
                    """
                )

        self.stdout.write(
            _("%(count)d '%(model)s' model(s) has been"
              " created.") % {
                  "model": CzechiaAccidents.__name__,
                  "count": CzechiaAccidents.objects.count() - accidents_count if
                  accidents_count else CzechiaAccidents.objects.count()}
        )

        # Create Poi
        self._create_cz_accidents_poi(query=query)

    def _get_datetime_message(self, end=False):
        """Get start/stop date time message

        :param bool end: get end date time message
        """
        if end:
            return self.end_date_message % {
                "datetime": timezone.now().strftime(self.datetime_format)
            } + "\n\n"
        return self.start_date_message % {
            "datetime": timezone.now().strftime(self.datetime_format)
        }

    def add_arguments(self, parser):
        parser.add_argument(
            "--geodata",
            dest="geodata",
            choices=("cz_regions", "cz_accidents_all", "cz_accidents_new"),
            help=_("Choose geodata for import"),
        )

    def handle(self, *args, **options):
        layer = options.get("geodata")

        layer_model_mapping = {
            "cz_regions": CzechiaRegions.__name__,
            "cz_accidents_all": CzechiaAccidents.__name__,
            "cz_accidents_new": CzechiaAccidents.__name__,
        }

        try_import_message = _("%(action)s '%(layer)s'"
                               " geodata model.") % {
                                   "layer": layer_model_mapping[layer],
                                   "action": "Updating" if layer in
                                   ("cz_accidents_new",) else "Importing"}
        sucess_import_message = _("%(action)s of geodata model '%(layer)s'"
                                  " has been successful.") % {
                                      "layer": layer_model_mapping[layer],
                                      "action": "Update" if layer in
                                      ("cz_accidents_new",) else "Import"}

        if layer == "cz_regions":
            with tempfile.TemporaryDirectory() as temp_dir:
                # CZ Regions (Kraje)
                self.stdout.write(self._get_datetime_message())
                self.stdout.write(try_import_message)
                self._import_cz_regions(temp_dir=temp_dir)
                self.stdout.write(self.style.SUCCESS(sucess_import_message))
                self.stdout.write(self._get_datetime_message(end=True))

        elif layer == "cz_accidents_all":
            with tempfile.TemporaryDirectory() as temp_dir:
                # CZ accidents all data
                self.stdout.write(self._get_datetime_message())
                self.stdout.write(try_import_message)
                self._import_cz_accidents(temp_dir=temp_dir)
                self.stdout.write(self.style.SUCCESS(sucess_import_message))
                self.stdout.write(self._get_datetime_message(end=True))

        elif layer == "cz_accidents_new":
            with tempfile.TemporaryDirectory() as temp_dir:
                # CZ accidents actual previous month data
                self.stdout.write(self._get_datetime_message())
                self.stdout.write(try_import_message)
                self._import_cz_accidents(temp_dir=temp_dir,
                                          actual_previous_month_only=True)
                self.stdout.write(self.style.SUCCESS(sucess_import_message))
                self.stdout.write(self._get_datetime_message(end=True))
