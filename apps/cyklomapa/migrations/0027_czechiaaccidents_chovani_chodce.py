# Generated by Django 2.2.24 on 2021-07-15 13:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cyklomapa', '0026_czechiaaccidents_kategorie_chodce'),
    ]

    operations = [
        migrations.AddField(
            model_name='czechiaaccidents',
            name='chovani_chodce',
            field=models.CharField(max_length=80, null=True),
        ),
    ]