# -*- coding: utf-8 -*-

from settings import *  # noqa

# Tento soubor překopírujte s názvem settings_local.py a doplňte vaše lokální nastavení

DEBUG = True
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG

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
GOOGLE_MAPS_API_KEY = 'abcdefg'

SECRET_KEY = 'change_me'


THUMBNAIL_DEBUG = True

# Make log in execution directory when testing
LOGGING['handlers']['logfile']['filename'] = normpath(PROJECT_DIR, "pnk.log")

EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = '/tmp/pnk-emails'

ALLOWED_HOSTS = [
    'mapa.prahounakole.cz',
    'localhost',
    "mapa.localhost",
    "testing-sector.testserver",
]

CSRF_COOKIE_SECURE = False
SECURE_BROWSER_XSS_FILTER = False
SECURE_CONTENT_TYPE_NOSNIFF = False
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
