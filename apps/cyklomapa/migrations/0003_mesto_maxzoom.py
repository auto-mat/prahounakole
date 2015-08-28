# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cyklomapa', '0002_auto_20150616_1610'),
    ]

    operations = [
        migrations.AddField(
            model_name='mesto',
            name='maxzoom',
            field=models.PositiveIntegerField(default=18, help_text='Maxim\xe1ln\xed zoomlevel mapy'),
        ),
    ]
