# Generated by Django 2.2.24 on 2021-07-08 07:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cyklomapa', '0010_czechiaaccidents_situovani'),
    ]

    operations = [
        migrations.RenameField(
            model_name='czechiaaccidents',
            old_name='priciny_nehody',
            new_name='priciny',
        ),
    ]
