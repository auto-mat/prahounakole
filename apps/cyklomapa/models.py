# -*- coding: utf-8 -*-

from django.contrib.gis.db import models
from django.utils.safestring import mark_safe
from django.core.cache import cache

from django.contrib.auth.models import User
from colorful.fields import RGBColorField

from .utils import SlugifyFileSystemStorage
from django.core.exceptions import ValidationError
from webmap.models import Sector, Marker

class Status(models.Model):
    "Stavy zobrazeni konkretniho objektu, vrstvy apod. - aktivni, navrzeny, zruseny, ..."
    nazev   = models.CharField(unique=True, max_length=255, help_text=u"Název statutu")
    desc    = models.TextField(null=True, blank=True, help_text=u"Popis")
    show    = models.BooleanField(help_text=u"Zobrazit uživateli zvenčí")
    show_TU = models.BooleanField(help_text=u"Zobrazit editorovi mapy")

    class Meta:
        verbose_name_plural = "statuty"
    def __unicode__(self):
        return self.nazev

def validate_slug(value):
    if value in ["P", "O", "C", "H", "G", "r"]:
        raise ValidationError(u'%s je již použité jako pro základní vrstvu. Prosím, nepoužívejte hodnoty: P, O, C, H, G, r' % value)

class Vrstva(models.Model):
    "Vrstvy, ktere se zobrazi v konkretni mape"
    nazev   = models.CharField(max_length=255)                      # Name of the layer
    slug    = models.SlugField(max_length=1, unique=True, validators=[ validate_slug ], verbose_name=u"Písmeno, které se objeví jako zkratka vrstvy v URL")  # Vrstva v URL
    desc    = models.TextField(null=True, blank=True)               # Description
    status  = models.ForeignKey(Status)              # zobrazovaci status
    order   = models.PositiveIntegerField()
    remark  = models.TextField(null=True, blank=True, help_text=u"interni informace o objektu, ktere se nebudou zobrazovat")
    enabled = models.BooleanField(verbose_name=u"Defaultně zapnuto", help_text=u"True = při načtení mapy se vrstva zobrazí jako zapnutá")

    class Meta:
        verbose_name_plural = u"vrstvy"
        ordering = ['order']
    def __unicode__(self):
        return self.nazev

class Znacka(models.Model):
    "Mapove znacky vcetne definice zobrazeni"
    nazev   = models.CharField(unique=True, max_length=255)   # Name of the mark
    slug    = models.SlugField(unique=True, verbose_name=u"název v URL")  # Vrstva v URL
    
    # Relationships
    vrstva  = models.ForeignKey(Vrstva)              # Kazda znacka lezi prave v jedne vrstve
    status  = models.ForeignKey(Status)              # kvuli vypinani
    
    # content 
    desc    = models.TextField(null=True, blank=True, help_text=u"podrobny popis znacky")
    remark  = models.TextField(null=True, blank=True, help_text=u"interni informace o objektu, ktere se nebudou zobrazovat")
    
    # Base icon and zoom dependent display range
    default_icon = models.ImageField(null=True, blank=True, upload_to='ikony', storage=SlugifyFileSystemStorage()) # XXX: zrusit null=True
    minzoom = models.PositiveIntegerField(default=1)
    maxzoom = models.PositiveIntegerField(default=10)

    # Linear elements style
    line_width = models.FloatField( verbose_name=u"šířka čáry", default=2,)
    line_color = RGBColorField(default="#ffc90e")
    def line_color_kml(this):
        color = this.line_color[1:]
        return "88" + color[4:6] + color[2:4] + color[0:2]

    url     = models.URLField(null=True, blank=True, help_text=u"ukáže se u všech míst s touto značkou, pokud nemají vlastní url")
    
    class Meta:
        permissions = [
            ("can_only_view", "Can only view"),
        ]
        verbose_name_plural = "značky"
        ordering = ['-vrstva__order', 'nazev']

    def __unicode__(self):
        return self.nazev

class ViditelneManager(models.GeoManager):
    "Pomocny manazer pro dotazy na Poi se zobrazitelnym statuem"
    def get_query_set(self):
        return super(ViditelneManager, self).get_query_set().filter(status__show=True, znacka__status__show=True)

class MarkerZnacka(models.Model):
    marker = models.OneToOneField(Marker, null=True)
    url = models.URLField(null=True, blank=True, help_text=u"ukáže se u všech míst s touto značkou, pokud nemají vlastní url")

class Mesto(models.Model):
    "Mesto - vyber na zaklade subdomeny"
    nazev         = models.CharField(unique=True, verbose_name=u"Název", max_length=255, blank=False)
    slug          = models.SlugField(unique=True, verbose_name=u"Subdoména v URL", blank=False)
    aktivni       = models.BooleanField(default=True, verbose_name=u"Aktivní", help_text=u"Město je přístupné pro veřejnost")
    vyhledavani   = models.BooleanField(verbose_name=u"Vyhledávač", help_text=u"Vyhledávání je aktivované")
    zoom          = models.PositiveIntegerField(default=13, help_text=u"Zoomlevel, ve kterém se zobrazí mapa po načtení")
    uvodni_zprava = models.TextField(null=True, blank=True, verbose_name=u"Úvodní zpráva", help_text=u"Zpráva, která se zobrazí v levém panelu")

    geom        = models.PointField(verbose_name=u"Poloha středu",srid=4326)
    sektor = models.OneToOneField(Sector, null=True)
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
    nazev   = models.CharField(max_length=255, verbose_name=u"název", help_text=u"Přesný název místa.")
    
    # Relationships
    znacka  = models.ForeignKey(Znacka, limit_choices_to = {'status__show_TU': 'True', 'vrstva__status__show_TU': 'True'}, verbose_name=u"značka", help_text="Zde vyberte ikonu, která se zobrazí na mapě.", related_name="pois")
    status  = models.ForeignKey(Status, default=3, help_text="Status místa; určuje, kde všude se místo zobrazí.")
    
    # "dulezitost" - modifikator minimalniho zoomu, ve kterem se misto zobrazuje. 
    dulezitost = models.SmallIntegerField(default=0, verbose_name=u"důležitost",
                 help_text=u"""Modifikátor minimalniho zoomu, ve kterém se místo zobrazuje (20+ bude vidět vždy).<br/>
                               Cíl je mít výběr základních objektů viditelných ve velkých měřítcích
                               a zabránit přetížení mapy značkami v přehledce.<br/>
                               Lze použít pro placenou reklamu! ("Váš podnik bude vidět hned po otevření mapy")""")
    
    # Geographical intepretation
    geom    = models.GeometryField(verbose_name=u"poloha",srid=4326, help_text=u"""Vložení bodu: Klikněte na tužku s plusem a umístěte bod na mapu<br/>
            Kreslení linie: Klikněte na ikonu linie a klikáním do mapy určete lomenou čáru. Kreslení ukončíte dvouklikem.<br/>
            Kreslení oblasti: Klikněte na ikonu oblasti a klikáním do mapy definujte oblast. Kreslení ukončíte dvouklikem.<br/>
            Úprava vložených objektů: Klikněte na první ikonu a potom klikněte na objekt v mapě. Tažením přesouváte body, body uprostřed úseků slouží k vkládání nových bodů do úseku.""")
    objects = models.GeoManager()
    
    # Own content (facultative)

    desc    = models.TextField(null=True, blank=True, verbose_name=u"popis", help_text=u"Text, který se zobrazí na mapě po kliknutí na ikonu.")
    desc_extra = models.TextField(null=True, blank=True, verbose_name=u"podrobný popis", help_text="Text, který rozšiřuje informace výše.")
    url     = models.URLField(null=True, blank=True, help_text=u"Odkaz na webovou stránku místa.")
    # address = models.CharField(max_length=255, null=True, blank=True)
    remark  = models.TextField(null=True, blank=True, verbose_name=u"interní poznámka", help_text=u"Interní informace o objektu, které se nebudou zobrazovat.")

    # navzdory nazvu jde o fotku v plnem rozliseni
    foto_thumb  = models.ImageField(null=True, blank=True,
                                    upload_to='foto', storage=SlugifyFileSystemStorage(),
                                    verbose_name=u"fotka",
                                    help_text=u"Nahrajte fotku v plné velikosti.",
                                   )

    mesto  = models.ForeignKey(Mesto, verbose_name=u"Město", default=1, help_text="Město, do kterého místo patří.")

    datum_zmeny = models.DateTimeField(auto_now=True, verbose_name=u"Datum poslední změny")
    
    viditelne = ViditelneManager()
    
    class Meta:
        verbose_name = "místo"
        verbose_name_plural = "místa"
    def __unicode__(self):
        if self.nazev:
            return self.nazev
        return unicode(self.znacka)
    def get_absolute_url(self):
        return "/misto/%i/" % self.id

    def has_change_permission(self, user):
       if user.is_superuser:
          return True
       return self.mesto in user.usermesto.mesta.all()

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

from django.db.models.signals import post_save, post_delete
def invalidate_cache(sender, instance, **kwargs):
    if sender in [Status, Vrstva, Znacka, Poi, Legenda]:
        cache.clear()
post_save.connect(invalidate_cache)
post_delete.connect(invalidate_cache)
    

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
