# Generated by Django 2.2.24 on 2021-07-15 07:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cyklomapa', '0021_czechiaaccidents_deleni_komunikace'),
    ]

    operations = [
        migrations.AddField(
            model_name='czechiaaccidents',
            name='rizeni_provozu_v_dobe_nehody',
            field=models.CharField(max_length=80, null=True),
        ),
    ]
