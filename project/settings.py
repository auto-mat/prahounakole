# Django global settings

# This allows us to construct the needed absolute paths dynamically,
# e.g., for the MEDIA_ROOT, and TEMPLATE_DIRS settings.
# see: http://rob.cogit8.org/blog/2008/Jun/20/django-and-relativity/
import os
import sys
normpath = lambda *args: os.path.normpath(os.path.abspath(os.path.join(*args)))
PROJECT_DIR = normpath(__file__, "..", "..")

sys.path.append(normpath(PROJECT_DIR, "project"))
sys.path.append(normpath(PROJECT_DIR, "apps"))

# http://docs.djangoproject.com/en/dev/topics/testing/#id1
# Your user must be a postgrest superuser
# Avoid specifying your password with: ~/.pgpass
# http://www.postgresql.org/docs/8.3/interactive/libpq-pgpass.html
TEST_RUNNER='django.contrib.gis.tests.run_gis_tests'

DEBUG = True
TEMPLATE_DEBUG = DEBUG
#COMPRESS = True

CACHES = {
	'default': {
		'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
		'LOCATION': '127.0.0.1:11211',
		'KEY_PREFIX': 'pnkvr',
	},
}


LANGUAGE_CODE = 'cs-cz'

TIME_ZONE = 'Europe/Prague'

SITE_ID = 1

USE_I18N = True

MEDIA_ROOT = 'media/'
MEDIA_URL = '/media/'

STATIC_ROOT = 'static/'
STATIC_URL = '/static/'
STATICFILES_DIRS = (
        os.path.join(PROJECT_DIR, 'apps/cyklomapa/static'),
)

from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS
TEMPLATE_CONTEXT_PROCESSORS += (
     'django.core.context_processors.request',
     'django.core.context_processors.media',
     'django.contrib.messages.context_processors.messages',
) 

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'cyklomapa.middleware.subdomains_middleware.SubdomainsMiddleware',
)

ROOT_URLCONF = 'urls'

# Python dotted path to the WSGI application used by Django's runserver.
#WSGI_APPLICATION = 'cyklomapa.wsgi.application'

TEMPLATE_DIRS = [
    os.path.join(PROJECT_DIR, 'templates'),
    os.path.join(PROJECT_DIR, 'apps/cyklomapa/templates'),
    os.path.join(PROJECT_DIR, 'olwidget/templates'),
    # Don't forget to use absolute paths, not relative paths.
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'cyklomapa',
    'easy_thumbnails',
    'django.contrib.humanize',
    'south',
    'smart_selects',
    'colorful',
]

ENABLE_API_PROXY = DEBUG        # http-roxy pro requesty na /api
PROXY_DOMAIN = 'www.cyclestreets.net'
