# Generated by Django 2.2.24 on 2021-07-22 10:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cyklomapa', '0034_czechiaaccidents_charakteristika_vozidla'),
    ]

    operations = [
        migrations.AddField(
            model_name='czechiaaccidents',
            name='smyk',
            field=models.CharField(max_length=10, null=True),
        ),
    ]