import json
import pathlib

from django.conf import settings
from django.core.management import BaseCommand
from django.utils.translation import gettext as _

from django_q.tasks import async_task

from cyklomapa.utils import check_download_cykliste_sobe_layer_job
from cyklomapa.views import get_cykliste_sobe_layer


class Command(BaseCommand):
    """Download cykliste sobe features JSON layer files"""
    help = "Download cykliste sobe features JSON layer files" # noqa

    def add_arguments(self, parser):
        parser.add_argument(
            "--task",
            dest="task",
            choices=("download_only",),
            help=_("Choose task"),
        )

    def handle(self, *args, **options):
        task = options.get("task")
        if task == "download_only":
            import importlib # noqa
            module, func = get_cykliste_sobe_layer.get_cs_features_layer_func.rsplit(".", 1)
            module = importlib.import_module(module)
            getattr(module, func)(
                cache_key=get_cykliste_sobe_layer.cache_key,
                cache_time=get_cykliste_sobe_layer.long_cache_time,
                save_to_file=get_cykliste_sobe_layer.features_file_path,
            )
        else:
            def download():
                async_task(func=get_cykliste_sobe_layer.get_cs_features_layer_func,
                           cache_key=get_cykliste_sobe_layer.cache_key,
                           cache_time=get_cykliste_sobe_layer.long_cache_time,
                           save_to_file=get_cykliste_sobe_layer.features_file_path,
                           save=True, sync=True)

            all_job_db_result, job_db_result, time_delta = \
                check_download_cykliste_sobe_layer_job()

            if job_db_result:
                if (time_delta.total_seconds() >= get_cykliste_sobe_layer.short_cache_time):
                    all_job_db_result.exclude(id=job_db_result.id).delete()
                    download()
                elif not get_cykliste_sobe_layer.features_file_path.is_file():
                    download()
            else:
                download()
