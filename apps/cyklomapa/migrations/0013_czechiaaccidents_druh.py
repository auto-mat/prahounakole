# Generated by Django 2.2.24 on 2021-07-14 08:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cyklomapa', '0012_czechiaaccidents_identifikacni_cislo'),
    ]

    operations = [
        migrations.AddField(
            model_name='czechiaaccidents',
            name='druh',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
