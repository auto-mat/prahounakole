# -*- coding: utf-8 -*-

from django.db import models


class EmailFilter(models.Model):
    email  = models.EmailField(verbose_name=u"Blokovaný email", null=True)
    active = models.BooleanField(help_text=u"Pravidlo je aktivní", default=True)
