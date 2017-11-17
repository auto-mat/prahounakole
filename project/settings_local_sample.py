# -*- coding: utf-8 -*-

import raven
from settings import *  # noqa
from settings import LOGGING, PROJECT_DIR, TEMPLATES, normpath

# Tento soubor překopírujte s názvem settings_local.py a doplňte vaše lokální nastavení

DEBUG = True
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG

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
GOOGLE_MAPS_API_KEY = 'abcdefg'

SECRET_KEY = 'change_me'

# Don't forget to use absolute paths, not relative paths.
# TEMPLATE_DIRS.append(os.path.join(PROJECT_DIR, 'env/lib/python2.6/site-packages/debug_toolbar/templates'))

# INSTALLED_APPS.append('debug_toolbar')


# def custom_show_toolbar(request):
#     return True  # Always show toolbar, for example purposes only.
#
# DEBUG_TOOLBAR_CONFIG = {
#     'SHOW_TOOLBAR_CALLBACK': custom_show_toolbar,
#     'HIDE_DJANGO_SQL': False,
# }

THUMBNAIL_DEBUG = True

ENABLE_API_PROXY = True

# Make log in execution directory when testing
LOGGING['handlers']['logfile']['filename'] = normpath(PROJECT_DIR, "pnk.log")

MEDIA_ROOT = 'media/'
STATIC_ROOT = 'static/'

EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = '/tmp/pnk-emails'

UGLIFY_JS_BINARY = "/usr/lib/node_modules/bower/node_modules/handlebars/node_modules/uglify-js/bin/uglifyjs"
# FORCE_SUBDOMAIN = "ostrava"

ALLOWED_HOSTS = [
    'mapa.prahounakole.cz',
    'localhost',
    "mapa.localhost",
]

# COMPRESS_ROOT = normpath(PROJECT_DIR, "apps/cyklomapa/static")
# COMPRESS_ENABLED = False

RAVEN_CONFIG = {
    'dsn': '',
    'release': raven.fetch_git_sha(PROJECT_DIR),
}

CSRF_COOKIE_SECURE = False
SECURE_BROWSER_XSS_FILTER = False
SECURE_CONTENT_TYPE_NOSNIFF = False
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
