# Generated by Django 2.2.24 on 2021-07-15 10:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cyklomapa', '0024_czechiaaccidents_specificka_mista_a_objekty_v_miste_nehody'),
    ]

    operations = [
        migrations.AddField(
            model_name='czechiaaccidents',
            name='smerove_pomery',
            field=models.CharField(max_length=100, null=True),
        ),
    ]