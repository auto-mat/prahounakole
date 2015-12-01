# -*- coding: utf-8 -*-

from settings import *

# Tento soubor překopírujte s názvem settings_local.py a doplňte vaše lokální nastavení

DEBUG = True
TEMPLATE_DEBUG = DEBUG

SERVER_EMAIL = 'pnk-technik@auto-mat.cz'
ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

DATABASES = {
        'default': {
                'ENGINE': 'django.contrib.gis.db.backends.postgis',
                'NAME': 'travis_ci_test',
                'USER': 'postgres',
                'PASSWORD': '',
                'HOST': 'localhost',
                'PORT': '',
        },
}

# Not used at this point but you'll need it here if you 
# want to enable a google maps baselayer within your
# OpenLayers maps
GOOGLE_MAPS_API_KEY='abcdefg'

SECRET_KEY = 'change_me'

# Don't forget to use absolute paths, not relative paths.
#TEMPLATE_DIRS.append(os.path.join(PROJECT_DIR, 'env/lib/python2.6/site-packages/debug_toolbar/templates'))

INSTALLED_APPS.append('debug_toolbar')

def custom_show_toolbar(request):
    return True # Always show toolbar, for example purposes only.

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': custom_show_toolbar,
    'HIDE_DJANGO_SQL': False,
}

THUMBNAIL_DEBUG = True

ENABLE_API_PROXY = True

#Make log in execution directory when testing
LOGGING['handlers']['logfile']['filename'] = normpath(PROJECT_DIR, "pnk.log")
