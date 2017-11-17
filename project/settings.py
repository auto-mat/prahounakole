# -*- coding: utf-8 -*-

# Django global settings

# This allows us to construct the needed absolute paths dynamically,
# e.g., for the MEDIA_ROOT, and TEMPLATE_DIRS settings.
# see: http://rob.cogit8.org/blog/2008/Jun/20/django-and-relativity/
import os
import re
import sys

from django.utils.translation import ugettext_lazy as _


def normpath(*args):
    return os.path.normpath(os.path.abspath(os.path.join(*args)))


PROJECT_DIR = normpath(__file__, "..", "..")

DEFAULT_FROM_EMAIL = 'Prahou na kole <redakce@prahounakole.cz>'

sys.path.append(normpath(PROJECT_DIR, "project"))
sys.path.append(normpath(PROJECT_DIR, "apps"))

DEBUG = True
# COMPRESS = True

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
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(PROJECT_DIR, 'templates'),
            os.path.join(PROJECT_DIR, 'apps/cyklomapa/templates'),
            os.path.join(PROJECT_DIR, 'olwidget/templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': (
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.request',
                'django.template.context_processors.media',
                'constance.context_processors.config',
                'django.contrib.messages.context_processors.messages',
            ),
            'debug': DEBUG,
        },
    },
]


MIDDLEWARE = (
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'raven.contrib.django.raven_compat.middleware.Sentry404CatchMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'cyklomapa.middleware.subdomains_middleware.SubdomainsMiddleware',
    'author.middlewares.AuthorDefaultBackendMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
)
MIDDLEWARE_CLASSES = MIDDLEWARE

ROOT_URLCONF = 'urls'

# Python dotted path to the WSGI application used by Django's runserver.
# WSGI_APPLICATION = 'cyklomapa.wsgi.application'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django.contrib.gis',

    'author',
    'adminsortable2',
    'constance.backends.database',
    'constance',
    'import_export',
    'webmap',
    'rest_framework',
    'leaflet',

    'feedback',
    'cyklomapa',
    'easy_thumbnails',
    'django.contrib.humanize',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'fluent_comments',
    'comments_moderation',
    'crispy_forms',
    'django_comments',
    'colorful',
    'massadmin',
    'compressor',
    'raven.contrib.django.raven_compat',
    'corsheaders',
    'httpproxy',
    'django_media_fixtures',
]

CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTOCOL', 'https')
SECURE_HSTS_SECONDS = 60
SECURE_SSL_REDIRECT = True
SECURE_REDIRECT_EXEMPT = [
    r"pnk.appcache",
    r"uzavirky/feed",
    r"novinky/feed",
]
SESSION_COOKIE_SECURE = True
X_FRAME_OPTIONS = 'DENY'

ENABLE_API_PROXY = DEBUG        # http-roxy pro requesty na /api
PROXY_BASE_URL = 'https://www.cyclestreets.net'

CONSTANCE_APP_NAME = "webmap"
CONSTANCE_CONFIG = {
    'MAP_BASELON': (14.4211, u'zeměpisná délka základní polohy mapy'),
    'MAP_BASELAT': (50.08741, u'zeměpisná délka základní polohy mapy'),
    'MAP_BOUNDS': ("14.22, 49.95, 14.8, 50.18", u'hranice zobrazení mapy'),
    'DEFAULT_STATUS_ID': (2, u'id defaultního statusu'),
    'ABOUT_MAP': ("Lorem ipsum", u'info o mapě'),
    'MAP_NEWS': ("Lorem ipsum", u'novinky mapy'),
}
CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'

CORS_ORIGIN_WHITELIST = (
    'cyklomapa.plzne.cz',
)
CORS_ORIGIN_REGEX_WHITELIST = (r'^(https?://)?(\w+\.)?prahounakole\.cz$', )

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'level': 'WARNING',
        'handlers': ['sentry'],
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s',
        },
        'simple': {
            'format': '%(levelname)s %(message)s',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'logfile': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': "/var/log/django/pnk.log",
            'backupCount': 50,
            'maxBytes': 10000000,
            'formatter': 'verbose',
        },
        'sentry': {
            'level': 'ERROR',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
            'tags': {'custom-tag': 'x'},
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        },
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
        },
        'raven': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
    },
}

THUMBNAIL_ALIASES = {
    '': {
        'photo_thumb': {'size': (514, 320), 'crop': 'smart'},
    },
}

REST_ENABLED = True

FLUENT_COMMENTS_EXCLUDE_FIELDS = ('url',)
COMMENTS_APP = 'fluent_comments'

COMPRESS_JS_COMPRESSOR = 'utils.uglify.UglifyJSCompressor'
UGLIFY_JS_BINARY = "uglifyjs"
COMPRESS_CACHE_BACKEND = 'default'
COMPRESS_PRECOMPILERS = (
    ('text/less', 'lessc {infile} {outfile}'),
)
COMPRESS_OFFLINE = True

TEST_RUNNER = 'cyklomapa.tests.CyklomapaTestSuiteRunner'

LEAFLET_CONFIG = {
    'DEFAULT_CENTER': (50.0866699218750000, 14.4387817382809995),
    'TILES': [
        (
            _(u'cyklomapa'),
            'http://tiles.prahounakole.cz/{z}/{x}/{y}.png',
            {'attribution': u'&copy; přispěvatelé <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'}),
        (
            _(u'Všeobecná mapa'),
            'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
            {'attribution': u'&copy; přispěvatelé <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'}),
    ],
    'DEFAULT_ZOOM': 8,
    'MIN_ZOOM': 8,
    'MAX_ZOOM': 18,
    'SPATIAL_EXTENT': [11.953, 48.517, 19.028, 51.097],
}

IGNORABLE_404_URLS = [
    re.compile(r'^/apple-touch-icon.*\.png$'),
    re.compile(r'^/favicon\.ico$'),
    re.compile(r'^/robots\.txt$'),
    re.compile(r'^/login\.php$'),
    re.compile(r'^/wp-login\.php$'),
    re.compile(r'^/shell\.php$'),
    re.compile(r'^/wordpress$'),
    re.compile(r'^/wp$'),
    re.compile(r'^/blog$'),
    re.compile(r'^/site$'),
    re.compile(r'^/blog/robots.txt$'),
    re.compile(r'^xmlrpc.php$'),
]

ALLOWED_HOSTS = ["localhost", "localhost:8000", "testing-sector.testserver"]

# import local settings
try:
    from settings_local import *  # noqa
except ImportError:
    pass
