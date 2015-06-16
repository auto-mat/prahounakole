# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cyklomapa', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='upresneni',
            name='email',
            field=models.EmailField(max_length=254, null=True, verbose_name='V\xe1\u0161 e-mail (pro dal\u0161\xed komunikaci)'),
        ),
    ]
