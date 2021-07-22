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


class CzechiaRegions(models.Model):
    """Czechia regions obtained from RUIAN DB.

    Load/update with 'loadgeodata' commnad.
    """
    gml_id = models.CharField(max_length=80)
    kod = models.IntegerField()
    nazev = models.CharField(max_length=80)
    nespravny = models.CharField(max_length=80)
    regionsoudrznostikod = models.IntegerField()
    platiod = models.CharField(max_length=80)
    platido = models.CharField(max_length=80)
    idtransakce = models.BigIntegerField()
    globalniidnavrhuzmeny = models.BigIntegerField()
    nutslau = models.CharField(max_length=80)
    datumvzniku = models.CharField(max_length=80)
    geom = models.MultiPolygonField(srid=4326)


# Auto-generated `LayerMapping` dictionary for CzechiaRegions model
czechiaregions_mapping = {
    'gml_id': 'gml_id',
    'kod': 'kod',
    'nazev': 'nazev',
    'nespravny': 'nespravny',
    'regionsoudrznostikod': 'regionsoudrznostikod',
    'platiod': 'platiod',
    'platido': 'platido',
    'idtransakce': 'idtransakce',
    'globalniidnavrhuzmeny': 'globalniidnavrhuzmeny',
    'nutslau': 'nutslau',
    'datumvzniku': 'datumvzniku',
    'geom': 'MULTIPOLYGON',
}


class CzechiaAccidents(models.Model):
    identifikacni_cislo = models.CharField(max_length=20, null=True)
    datum = models.DateField(null=True)
    den = models.CharField(max_length=2, null=True)
    cas = models.TimeField(null=True)
    druh = models.CharField(max_length=50, null=True)
    druh_srazky_jedoucich_vozidel = models.CharField(max_length=80, null=True)
    lokalita = models.CharField(max_length=20, null=True)
    nasledky = models.CharField(max_length=20, null=True)
    zavineni = models.CharField(max_length=50, null=True)
    alkohol_u_vinika_nehody_pritomen = models.CharField(max_length=50, null=True)
    priciny = models.CharField(max_length=500, null=True)
    druh_povrchu_vozovky = models.CharField(max_length=30, null=True)
    stav_povrchu_vozovky_v_dobe_nehody = models.CharField(max_length=80, null=True)
    stav_komunikace = models.CharField(max_length=80, null=True)
    viditelnost = models.CharField(max_length=120, null=True)
    deleni_komunikace = models.CharField(max_length=50, null=True)
    situovani = models.CharField(max_length=50, null=True)
    rizeni_provozu_v_dobe_nehody = models.CharField(max_length=80, null=True)
    mistni_uprava_prednosti_v_jizde = models.CharField(max_length=100, null=True)
    specificka_mista_a_objekty_v_miste_nehody = models.CharField(max_length=100, null=True)
    smerove_pomery = models.CharField(max_length=100, null=True)
    pocet_zucastnenych_vozidel = models.IntegerField(null=True)
    misto_dopravni_nehody = models.CharField(max_length=220, null=True)
    druh_pozemni_komunikace = models.CharField(max_length=80, null=True)
    druh_krizujici_komunikace = models.CharField(max_length=50, null=True)
    kategorie_chodce = models.CharField(max_length=20, null=True)
    chovani_chodce = models.CharField(max_length=80, null=True)
    situace_v_miste_nehody = models.CharField(max_length=80, null=True)
    druh_vozidla = models.CharField(max_length=100, null=True)
    geom = models.PointField(srid=4326)


czechiaaccidents_mapping = {
    'identifikacni_cislo': 'identifikacni_cislo',
    'datum': 'datum',
    'den': 'den',
    'cas': 'cas',
    'druh': 'druh',
    'druh_srazky_jedoucich_vozidel': 'druh_srazky_jedoucich_vozidel',
    'lokalita': 'lokalita',
    'nasledky': 'nasledky',
    'zavineni': 'zavineni',
    'alkohol_u_vinika_nehody_pritomen': 'alkohol_u_vinika_nehody_pritomen',
    'priciny': 'priciny',
    'druh_povrchu_vozovky': 'druh_povrchu_vozovky',
    'stav_povrchu_vozovky_v_dobe_nehody': 'stav_povrchu_vozovky_v_dobe_nehody',
    'stav_komunikace': 'stav_komunikace',
    'viditelnost': 'viditelnost',
    'deleni_komunikace': 'deleni_komunikace',
    'situovani': 'situovani',
    'rizeni_provozu_v_dobe_nehody': 'rizeni_provozu_v_dobe_nehody',
    'mistni_uprava_prednosti_v_jizde': 'mistni_uprava_prednosti_v_jizde',
    'specificka_mista_a_objekty_v_miste_nehody': 'specificka_mista_a_objekty_v_miste_nehody',
    'smerove_pomery': 'smerove_pomery',
    'pocet_zucastnenych_vozidel': 'pocet_zucastnenych_vozidel',
    'misto_dopravni_nehody': 'misto_dopravni_nehody',
    'druh_pozemni_komunikace': 'druh_pozemni_komunikace',
    'druh_krizujici_komunikace': 'druh_krizujici_komunikace',
    'kategorie_chodce': 'kategorie_chodce',
    'chovani_chodce': 'chovani_chodce',
    'situace_v_miste_nehody': 'situace_v_miste_nehody',
    'druh_vozidla': 'druh_vozidla',
    'geom': 'POINT',
}
