# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.contrib.gis.db import models

from webmap.models import Marker, Poi, Sector


class Poi(Poi):
    class Meta:
        proxy = True

    def get_absolute_url(self):
        return "#misto=%s_%i/" % (self.marker.layer.slug, self.id)


class MarkerZnacka(models.Model):
    marker = models.OneToOneField(Marker, null=True, on_delete=models.CASCADE)
    url = models.URLField(null=True, blank=True, help_text=u"ukáže se u všech míst s touto značkou, pokud nemají vlastní url")


class Mesto(models.Model):
    "Mesto - vyber na zaklade subdomeny"
    aktivni = models.BooleanField(default=True, verbose_name=u"Aktivní", help_text=u"Město je přístupné pro veřejnost")
    vyhledavani = models.BooleanField(verbose_name=u"Vyhledávač", default=True, help_text=u"Vyhledávání je aktivované")
    zoom = models.PositiveIntegerField(default=13, help_text=u"Zoomlevel, ve kterém se zobrazí mapa po načtení")
    maxzoom = models.PositiveIntegerField(default=18, help_text=u"Maximální zoomlevel mapy")
    uvodni_zprava = models.TextField(null=True, blank=True, verbose_name=u"Úvodní zpráva", help_text=u"Zpráva, která se zobrazí v levém panelu")

    geom = models.PointField(verbose_name=u"Poloha středu", srid=4326)
    sektor = models.OneToOneField(Sector, null=True, on_delete=models.CASCADE)

    class Meta:
        permissions = [
            ("can_edit_all_fields", "Can edit all field"),
        ]
        verbose_name_plural = "města"

    def __str__(self):
        return self.sektor.name


class UserMesto(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mesta = models.ManyToManyField(Mesto)


UPRESNENI_CHOICE = (
    ('novy', u'Nový'),
    ('reseno', u'V řešení'),
    ('vyreseno', u'Vyřešeno'),
    ('zamitnuto', u'Zamítnuto'),
)


class Upresneni(models.Model):
    """
    Tabulka pro uzivatelske doplnovani informaci do mapy.

    Prozatim na principu rucniho prepisu udaju v adminu.
    Vyzchazi z POI, ale nekopiruje se do ni.
    Slouzi predevsim k doplneni informace k mistu. Nektera pole mohou byt proto nefunkncni.
    Pouziva se pouze v Zelene mape, v PNK zatim neaktivni
    """

    misto = models.ForeignKey(Poi, blank=True, null=True, on_delete=models.CASCADE)  # Odkaz na objekt, ktery chce opravit, muze byt prazdne.
    email = models.EmailField(verbose_name=u"Váš e-mail (pro další komunikaci)", null=True)    # Prispevatel musi vyplnit email.
    status = models.CharField(max_length=10, choices=UPRESNENI_CHOICE)
    desc = models.TextField(verbose_name=u"Popis (doplnění nebo oprava nebo popis nového místa, povinné pole)", null=True)
    url = models.URLField(verbose_name=u"Odkaz, webové stránky místa (volitelné pole)", null=True, blank=True)  # Odkaz z vypisu - stranka podniku apod.
    address = models.CharField(verbose_name=u"Adresa místa, popis lokace (volitelné pole)", max_length=255, null=True, blank=True)

    class Meta:
        verbose_name_plural = u"upřesnění"

    def __str__(self):
        return u"%s - %s" % (self.misto, self.email)
