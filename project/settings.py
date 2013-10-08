# Django global settings

# This allows us to construct the needed absolute paths dynamically,
# e.g., for the MEDIA_ROOT, and TEMPLATE_DIRS settings.
# see: http://rob.cogit8.org/blog/2008/Jun/20/django-and-relativity/
import os
import sys
normpath = lambda *args: os.path.normpath(os.path.abspath(os.path.join(*args)))
PROJECT_DIR = normpath(__file__, "..", "..")

DEFAULT_FROM_EMAIL = 'Prahou na kole <redakce@prahounakole.cz>'

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
		'KEY_PREFIX': 'pnk-map',
	},
}


LANGUAGE_CODE = 'cs-cz'

TIME_ZONE = 'Europe/Prague'

SITE_ID = 1

USE_I18N = True

MEDIA_ROOT = os.path.join(PROJECT_DIR, 'media/')
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(PROJECT_DIR, 'static/')
STATIC_URL = '/static/'
LOGIN_URL = '/admin/'
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
    'django.middleware.csrf.CsrfViewMiddleware',
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
    'colorful',
    'django.contrib.sites',
    'fluent_comments',
    'comments_moderation',
    'crispy_forms',
    'django.contrib.comments',
    'massadmin',
]

ENABLE_API_PROXY = DEBUG        # http-roxy pro requesty na /api
PROXY_BASE_URL = 'http://www.cyclestreets.net'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
         'require_debug_false': {
             '()': 'django.utils.log.RequireDebugFalse'
         }
     },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'django.utils.log.NullHandler',
        },
        'console':{
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'logfile': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': "/var/log/django/pnk.log",
            'backupCount': 50,
            'maxBytes': 10000000,
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'logfile'],
            'propagate': True,
            'level': 'INFO',
        },
        'django.request': {
            'handlers': ['mail_admins', 'logfile'],
            'level': 'ERROR',
            'propagate': False,
        },
        'cyklomapa': {
            'handlers': ['console', 'mail_admins', 'logfile'],
            'level': 'INFO',
        }
    }
}

# import local settings
try:
    from settings_local import *
except ImportError:
    pass
