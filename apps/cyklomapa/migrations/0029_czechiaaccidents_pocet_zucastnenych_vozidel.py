# Generated by Django 2.2.24 on 2021-07-21 10:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cyklomapa', '0028_czechiaaccidents_situace_v_miste_nehody'),
    ]

    operations = [
        migrations.AddField(
            model_name='czechiaaccidents',
            name='pocet_zucastnenych_vozidel',
            field=models.IntegerField(null=True),
        ),
    ]
