# Generated by Django 2.2.24 on 2021-07-21 07:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cyklomapa', '0027_czechiaaccidents_chovani_chodce'),
    ]

    operations = [
        migrations.AddField(
            model_name='czechiaaccidents',
            name='situace_v_miste_nehody',
            field=models.CharField(max_length=80, null=True),
        ),
    ]
