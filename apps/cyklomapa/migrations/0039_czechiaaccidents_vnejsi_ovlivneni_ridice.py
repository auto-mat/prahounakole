# Generated by Django 2.2.24 on 2021-07-22 14:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cyklomapa', '0038_czechiaaccidents_stav_ridice'),
    ]

    operations = [
        migrations.AddField(
            model_name='czechiaaccidents',
            name='vnejsi_ovlivneni_ridice',
            field=models.CharField(max_length=80, null=True),
        ),
    ]
