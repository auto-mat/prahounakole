# Generated by Django 2.2.24 on 2021-07-14 10:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cyklomapa', '0015_auto_20210714_1040'),
    ]

    operations = [
        migrations.AddField(
            model_name='czechiaaccidents',
            name='alkohol_u_vinika_nehody_pritomen',
            field=models.CharField(max_length=50, null=True),
        ),
    ]