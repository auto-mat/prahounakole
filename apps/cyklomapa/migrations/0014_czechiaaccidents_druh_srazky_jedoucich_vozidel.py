# Generated by Django 2.2.24 on 2021-07-14 08:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cyklomapa', '0013_czechiaaccidents_druh'),
    ]

    operations = [
        migrations.AddField(
            model_name='czechiaaccidents',
            name='druh_srazky_jedoucich_vozidel',
            field=models.CharField(max_length=20, null=True),
        ),
    ]