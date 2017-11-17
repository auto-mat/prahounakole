# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.contrib.gis.db.models.fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('webmap', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='MarkerZnacka',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.URLField(help_text='uk\xe1\u017ee se u v\u0161ech m\xedst s touto zna\u010dkou, pokud nemaj\xed vlastn\xed url', null=True, blank=True)),
                ('marker', models.OneToOneField(null=True, to='webmap.Marker', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Mesto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('aktivni', models.BooleanField(default=True, help_text='M\u011bsto je p\u0159\xedstupn\xe9 pro ve\u0159ejnost', verbose_name='Aktivn\xed')),
                ('vyhledavani', models.BooleanField(default=True, help_text='Vyhled\xe1v\xe1n\xed je aktivovan\xe9', verbose_name='Vyhled\xe1va\u010d')),
                ('zoom', models.PositiveIntegerField(default=13, help_text='Zoomlevel, ve kter\xe9m se zobraz\xed mapa po na\u010dten\xed')),
                ('uvodni_zprava', models.TextField(help_text='Zpr\xe1va, kter\xe1 se zobraz\xed v lev\xe9m panelu', null=True, verbose_name='\xdavodn\xed zpr\xe1va', blank=True)),
                ('geom', django.contrib.gis.db.models.fields.PointField(srid=4326, verbose_name='Poloha st\u0159edu')),
                ('sektor', models.OneToOneField(null=True, to='webmap.Sector', on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name_plural': 'm\u011bsta',
                'permissions': [('can_edit_all_fields', 'Can edit all field')],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Upresneni',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.EmailField(max_length=75, null=True, verbose_name='V\xe1\u0161 e-mail (pro dal\u0161\xed komunikaci)')),
                ('status', models.CharField(max_length=10, choices=[(b'novy', 'Nov\xfd'), (b'reseno', 'V \u0159e\u0161en\xed'), (b'vyreseno', 'Vy\u0159e\u0161eno'), (b'zamitnuto', 'Zam\xedtnuto')])),
                ('desc', models.TextField(null=True, verbose_name='Popis (dopln\u011bn\xed nebo oprava nebo popis nov\xe9ho m\xedsta, povinn\xe9 pole)')),
                ('url', models.URLField(null=True, verbose_name='Odkaz, webov\xe9 str\xe1nky m\xedsta (voliteln\xe9 pole)', blank=True)),
                ('address', models.CharField(max_length=255, null=True, verbose_name='Adresa m\xedsta, popis lokace (voliteln\xe9 pole)', blank=True)),
                ('misto', models.ForeignKey(blank=True, to='webmap.Poi', null=True, on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name_plural': 'up\u0159esn\u011bn\xed',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserMesto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('mesta', models.ManyToManyField(to='cyklomapa.Mesto')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
