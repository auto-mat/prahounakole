# -*- coding: utf-8 -*-

import json
import os
import requests
import threading

from django.core.cache import cache
from django.core.files.storage import FileSystemStorage
from django.template.defaultfilters import slugify


class SlugifyFileSystemStorage(FileSystemStorage):
    "Storage, ktery odstrani diakritiku a dalsi balast v nazvu souboru"
    def get_valid_name(self, name):
        name, ext = os.path.splitext(name)
        return slugify(name) + ext


def parse_cykliste_sobe_features(cache_key=None, cache_time=None,
                                 save_to_file=None):
    """Parse downloaded cykliste sobe features layer JSON

    :param cache_key str: cache key name for result cykleste sobe features
    layer dict
    :param cache_time float: number of seconds for caching result
    cykleste sobe features layer dict
    :param save_to_file str: file path where cykliste sobe features
    layer JSON will be saved

    :return result dict: cykleste sobe features layer dict
    """

    def download_json_file(page, lock, result):
        """Download cykleste sobe layer features (JSON file)

        :param lock obj: thread lock
        :param result list: append loaded cykliste sobe JSON features
        layer into list

        :return str: number of cykliste sobe layer REST API pages
        """
        r = requests.get(f"http://www.cyklistesobe.cz/api/issues/?page={page}")
        with lock:
            result.append(json.loads(r.content))
        if "X-Total-Pages" in r.headers.keys():
            return r.headers["X-Total-Pages"]

    def download_features(pages, features, lock):
        """Download cykliste sobe features layer JSON files using threads

        :param pages int: number of cykliste sobe REST API pages
        :param lock obj: thread lock
        :param features list: append loaded cykliste sobe JSON features
        layer into list

        :return files list: cykliste sobe features layer JSON files list
        """
        threads = []
        for p in range(2, pages + 1):
            t = threading.Thread(
                target=download_json_file,
                args=(p, lock, features),
                daemon=True,
            )
            t.start()
            threads.append(t)
        for t in threads:
            t.join()
        return features

    def parse_and_merge_jsons(jsons, result):
        """Parse and merge cyklsite sobe features layer JSONs

        :param jsons list: list of cykliste sobe layers JSONs
        :param result dict:
        """
        for j in jsons:
            result["features"].extend(j["features"])

    result = {
        "type": "FeatureCollection",
        "features": [],
    }
    features = []
    lock = threading.Lock()
    pages = int(download_json_file(page=1, lock=lock,
                                   result=features))
    parse_and_merge_jsons(download_features(pages, features, lock),
                          result)
    if cache_key:
        cache.set(cache_key, result, cache_time)

    if save_to_file and pathlib.Path(save_to_file).is_file:
        with open(save_to_file, "w") as f:
            json.dump(result, f)

    return result
