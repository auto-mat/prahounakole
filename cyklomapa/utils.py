# -*- coding: utf-8 -*-

import os
from django.core.files.storage import FileSystemStorage
from django.template.defaultfilters import slugify

class SlugifyFileSystemStorage(FileSystemStorage):
    "Storage, ktery odstrani diakritiku a dalsi balast v nazvu souboru"
    def get_valid_name(self, name):
        name, ext = os.path.splitext(name)
        return slugify(name) + ext
