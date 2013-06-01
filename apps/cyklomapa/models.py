# -*- coding: utf-8 -*-

from django.contrib.gis.db import models
from django.utils.safestring import mark_safe
from django.core.cache import cache
from django.contrib.auth.models import User
from smart_selects.db_fields import GroupedForeignKey

from .utils import SlugifyFileSystemStorage

class Status(models.Model):
    "stavy zobrazeni konkretniho objektu, vrstvy apod. - aktivni, navrzeny, zruseny, ..."
    nazev   = models.CharField(unique=True, max_length=255)         # Nazev statutu
    desc    = models.TextField(null=True, blank=True)               # Description
    show    = models.BooleanField()                                 # Zobrazit uzivateli zvenci
    show_TU = models.BooleanField()                                 # Zobrazit editorovi mapy

    class Meta:
        verbose_name_plural = "statuty"
    def __unicode__(self):
        return self.nazev

class Vrstva(models.Model):
    "vrstvy, ktere se zobrazi v konkretni mape"
    nazev   = models.CharField(max_length=255)                      # Name of the layer
    slug    = models.SlugField(unique=True, verbose_name=u"Název v URL")  # Vrstva v URL
    desc    = models.TextField(null=True, blank=True)               # Description
    status  = models.ForeignKey(Status)              # zobrazovaci status
    order   = models.PositiveIntegerField()
    remark  = models.TextField(null=True, blank=True) # Interni informace o objektu, ktere se nebudou zobrazovat!
    enabled = models.BooleanField()                                 # Vrstva je defaultně zobrazená

    class Meta:
        verbose_name_plural = "vrstvy"
        ordering = ['order']
    def __unicode__(self):
        return self.nazev

    
class Znacka(models.Model):
    "mapove znacky vcetne definice zobrazeni"
    nazev   = models.CharField(unique=True, max_length=255)   # Name of the mark
    slug    = models.SlugField(unique=True, verbose_name=u"název v URL")  # Vrstva v URL
    
    # Relationships
    vrstva  = models.ForeignKey(Vrstva)              # Kazda znacka lezi prave v jedne vrstve
    status  = models.ForeignKey(Status)              # kvuli vypinani
    
    # content 
    desc    = models.TextField(null=True, blank=True) # podrobny popis znacky
    remark  = models.TextField(null=True, blank=True) # Interni informace o objektu, ktere se nebudou zobrazovat!
    
    # Base icon and zoom dependent display range
    default_icon = models.ImageField(null=True, upload_to='ikony', storage=SlugifyFileSystemStorage()) # XXX: zrusit null=True
    minzoom = models.PositiveIntegerField(default=1)
    maxzoom = models.PositiveIntegerField(default=10)

    url     = models.URLField(null=True, blank=True, help_text=u"ukáže se u všech míst s touto značkou, pokud nemají vlastní url")
    
    class Meta:
        verbose_name_plural = "značky"
        ordering = ['-vrstva__order', 'nazev']

    def __unicode__(self):
        return self.nazev

class ViditelneManager(models.GeoManager):
    "Pomocny manazer pro dotazy na Poi se zobrazitelnym statuem"
    def get_query_set(self):
        return super(ViditelneManager, self).get_query_set().filter(status__show=True, znacka__status__show=True)

class Mesto(models.Model):
    "Mesto - vyber na zaklade subdomeny"
    nazev         = models.CharField(unique=True, verbose_name=u"Název", max_length=255, blank=False)
    slug          = models.SlugField(unique=True, verbose_name=u"Subdoména v URL", blank=False)
    aktivni       = models.BooleanField(default=True, verbose_name=u"Aktivní", help_text=u"Město je přístupné pro veřejnost")
    vyhledavani   = models.BooleanField(verbose_name=u"Vyhledávač", help_text=u"Vyhledávání je aktivované")
    zoom          = models.PositiveIntegerField(default=13, help_text=u"Zoomlevel, ve kterém se zobrazí mapa po načtení")
    uvodni_zprava = models.TextField(null=True, blank=True, verbose_name=u"Úvodní zpráva", help_text=u"Zpráva, která se zobrazí v levém panelu")

    geom        = models.PointField(verbose_name=u"Poloha středu",srid=4326)
    objects = models.GeoManager()

    class Meta:
        verbose_name_plural = "města"
    def __unicode__(self):
        return self.nazev

class UserMesto(models.Model):
    user = models.OneToOneField(User)
    mesta = models.ManyToManyField(Mesto)

class Poi(models.Model):
    "Misto - bod v mape"
    nazev   = models.CharField(max_length=255, verbose_name=u"Název", blank=True)   # Name of the location
    
    # Relationships
    vrstva  = 0                                                          # Pole používané smart_selects
    znacka  = GroupedForeignKey(Znacka, "vrstva", verbose_name=u"Značka")# "Znacky"   - misto ma prave jednu
    status  = models.ForeignKey(Status, verbose_name=u"Status")          # "Statuty"  - misto ma prave jeden
    
    # "dulezitost" - modifikator minimalniho zoomu, ve kterem se misto zobrazuje. 
    # Cim vetsi, tim vice bude poi videt, +20 = bude videt vydycky
    # Cil je mit vyber zakladnich objektu viditelnych ve velkych meritcich
    # a zabranit pretizeni mapy znackami v prehledce.
    # Lze pouzit pro placenou reklamu! ("Vas podnik bude videt hned po otevreni mapy")
    dulezitost = models.SmallIntegerField(default=0)
    
    # Geographical intepretation
    geom    = models.PointField(verbose_name=u"Poloha",srid=4326)
    objects = models.GeoManager()
    
    # Own content (facultative)
    desc    = models.TextField(null=True, verbose_name=u"Popis", blank=True)
    desc_extra = models.TextField(null=True, verbose_name=u"Extra popis", blank=True, help_text="text do podrobnějšího výpisu bodu (mimo popup)")
    url     = models.URLField(null=True, verbose_name=u"Odkaz URL", blank=True)  # Odkaz z vypisu - stranka podniku apod.
    # address = models.CharField(max_length=255, null=True, blank=True)
    remark  = models.TextField(null=True, verbose_name=u"Poznámka", blank=True, help_text="Interni informace o objektu, ktere se nebudou zobrazovat!")

    # navzdory nazvu jde o fotku v plnem rozliseni
    foto_thumb  = models.ImageField(verbose_name=u"fotka", null=True, blank=True,
                                    upload_to='foto', storage=SlugifyFileSystemStorage())

    mesto  = models.ForeignKey(Mesto, verbose_name=u"Město", default=1)           # Město, do kterého místo patří

    datum_zmeny = models.DateTimeField(auto_now=True, verbose_name=u"Datum poslední změny")
    
    viditelne = ViditelneManager()
    
    class Meta:
        verbose_name_plural = "místa"
    def __unicode__(self):
        if self.nazev:
            return self.nazev
        return unicode(self.znacka)
    def get_absolute_url(self):
        return "/misto/%i/" % self.id

class Legenda(models.Model):
    "prvky legendy mapoveho podkladu"
    nazev   = models.CharField(unique=True, max_length=255)
    slug    = models.SlugField(unique=True, verbose_name=u"název v URL")
    popis    = models.TextField(null=True, blank=True)
    obrazek = models.ImageField(upload_to='ikony', storage=SlugifyFileSystemStorage())
    class Meta:
        verbose_name_plural = u"legenda"
    def __unicode__(self):
        return self.nazev

from django.db.models.signals import post_save
def invalidate_cache(sender, instance, **kwargs):
    if sender in [Status, Vrstva, Znacka, Poi, Legenda]:
        cache.clear()
post_save.connect(invalidate_cache)
    

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

    misto  = models.ForeignKey(Poi, blank=True, null=True) # Odkaz na objekt, ktery chce opravit, muze byt prazdne.
    email  = models.EmailField(verbose_name=u"Váš e-mail (pro další komunikaci)", null=True)    # Prispevatel musi vyplnit email.
    status  = models.CharField(max_length=10,choices=UPRESNENI_CHOICE) 
    desc    = models.TextField(verbose_name=u"Popis (doplnění nebo oprava nebo popis nového místa, povinné pole)",null=True)
    url     = models.URLField(verbose_name=u"Odkaz, webové stránky místa (volitelné pole)",null=True, blank=True)  # Odkaz z vypisu - stranka podniku apod.
    address = models.CharField(verbose_name=u"Adresa místa, popis lokace (volitelné pole)",max_length=255, null=True, blank=True)

    class Meta:
        verbose_name_plural = u"upřesnění"
    def __unicode__(self):
        return u"%s - %s" % (self.misto, self.email)
