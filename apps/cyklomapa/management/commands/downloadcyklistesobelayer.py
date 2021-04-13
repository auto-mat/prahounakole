import json
import pathlib

from django.conf import settings
from django.core.management import BaseCommand

from django_q.tasks import async_task

from cyklomapa.utils import (
    check_download_cykliste_sobe_layer_job, parse_cykliste_sobe_features,
)
from cyklomapa.views import get_cyklisty_sobe_layer


class Command(BaseCommand):
    """Download cykliste sobe features JSON layer files"""
    help = "Download cykliste sobe features JSON layer files" # noqa

    def handle(self, *args, **options):
        def download():
            async_task(func=get_cyklisty_sobe_layer.get_cs_features_layer_func,
                       cache_key=get_cyklisty_sobe_layer.cache_key,
                       cache_time=get_cyklisty_sobe_layer.long_cache_time,
                       save_to_file=get_cyklisty_sobe_layer.features_file_path,
                       save=True)

        all_job_db_result, job_db_result, time_delta = \
            check_download_cykliste_sobe_layer_job()

        if job_db_result:
            if (time_delta.total_seconds() >= get_cyklisty_sobe_layer.short_cache_time):
                download()
            elif not get_cyklisty_sobe_layer.features_file_path.is_file():
                download()
        else:
            download()
