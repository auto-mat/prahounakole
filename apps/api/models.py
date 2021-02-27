from django.contrib.auth.models import Group
from django.db import models

# Create your models here.


class ScopesDefinition(models.Model):
    scope = models.CharField(max_length=300)
    description = models.CharField(max_length=500)

    def __str__(self):
        return self.scope


class Scopes(models.Model):
    group = models.ManyToManyField(Group)
    scopes = models.ManyToManyField(ScopesDefinition)
    description = models.CharField(max_length=500)

    def __str__(self):
        return ' '.join(
            list(
                self.scopes.all().values_list('scope', flat=True),
            ),
        )
