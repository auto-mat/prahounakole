# Generated by Django 2.2.24 on 2021-07-14 11:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cyklomapa', '0016_czechiaaccidents_alkohol_u_vinika_nehody_pritomen'),
    ]

    operations = [
        migrations.AddField(
            model_name='czechiaaccidents',
            name='druh_povrchu_vozovky',
            field=models.CharField(max_length=30, null=True),
        ),
    ]
