# Generated by Django 2.2.24 on 2021-07-08 05:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cyklomapa', '0008_czechiaaccidents_priciny_nehody'),
    ]

    operations = [
        migrations.AddField(
            model_name='czechiaaccidents',
            name='lokalita',
            field=models.CharField(max_length=20, null=True),
        ),
    ]
