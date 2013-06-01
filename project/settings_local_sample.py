# -*- coding: utf-8 -*-

from settings import *

# Sem doplňte vaše lokální nastavení
DATABASES = {
        'default': {
                'ENGINE': 'django.contrib.gis.db.backends.postgis',
                'NAME': '',
                'USER': '',
                'PASSWORD': '',
                'HOST': 'localhost',
                'PORT': '',
        },
}

# Not used at this point but you'll need it here if you 
# want to enable a google maps baselayer within your
# OpenLayers maps
GOOGLE_MAPS_API_KEY='abcdefg'

MEDIA_URL = 'http://mapa.prahounakole.cz/media/'

SECRET_KEY = ''

# Don't forget to use absolute paths, not relative paths.
TEMPLATE_DIRS.append(os.path.join(PROJECT_DIR, 'env/lib/python2.6/site-packages/debug_toolbar/templates'))

INSTALLED_APPS.append('debug_toolbar')

def custom_show_toolbar(request):
    return True # Always show toolbar, for example purposes only.

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': custom_show_toolbar,
    'HIDE_DJANGO_SQL': False,
}

THUMBNAIL_DEBUG = True

ENABLE_API_PROXY = False
