# -*- coding: utf-8 -*-

# Django global settings

# This allows us to construct the needed absolute paths dynamically,
# e.g., for the MEDIA_ROOT, and TEMPLATE_DIRS settings.
# see: http://rob.cogit8.org/blog/2008/Jun/20/django-and-relativity/
import os
import re
import sys


from django.utils.translation import ugettext_lazy as _

import raven


def normpath(*args):
    return os.path.normpath(os.path.abspath(os.path.join(*args)))


PROJECT_DIR = normpath(__file__, "..", "..", "..")
BASE_DIR = PROJECT_DIR

DEFAULT_FROM_EMAIL = 'Prahou na kole <redakce@prahounakole.cz>'

sys.path.append(normpath(PROJECT_DIR, "project"))
sys.path.append(normpath(PROJECT_DIR, "apps"))

DEBUG = os.environ.get("DEBUG", False) in (True, "True")
# COMPRESS = True

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.environ.get("DB_NAME", 'pnk'),
        'USER': os.environ.get("DB_USER", 'pnk'),
        'PASSWORD': os.environ.get("DB_PASSWORD", 'foobar'),
        'HOST': os.environ.get("DB_HOST", 'postgres'),
        'PORT': os.environ.get("DB_PORT", ''),
    },
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        'KEY_PREFIX': 'pnk-map',
    },
}

SECRET_KEY = os.environ.get('SECRET_KEY', '')

LANGUAGE_CODE = 'cs-cz'

TIME_ZONE = 'Europe/Prague'

SITE_ID = 1

USE_I18N = True

MEDIA_ROOT = os.environ.get('S3_MEDIA_ROOT', normpath(PROJECT_DIR, 'media/'))

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
    'djangobower.finders.BowerFinder',
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
    'whitenoise.middleware.WhiteNoiseMiddleware',
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
    'storages',
    'inline_static',

    'feedback',
    'cyklomapa',
    'easy_thumbnails',
    'django.contrib.humanize',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'captcha',
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
    'djangobower',
    'oauth2_provider',
]

FLUENT_COMMENTS_FORM_CLASS = 'fluent_comments.forms.captcha.DefaultCommentForm'  # default

CAPTCHA_NOISE_FUNCTIONS = ()
CAPTCHA_FONT_SIZE = 30
CAPTCHA_LETTER_ROTATION = (-10, 10)

BOWER_INSTALLED_APPS = (
    "lightbox#2.11.1",
    "css-browser-selector",
    "jqueryui#1.12.1",
    "jquery#3.4.1",
    "https://github.com/PetrDlouhy/ol2.git",
    "bootstrap#3.4.1",
    "https://github.com/commonpike/jquery-persist.git",
)

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

ENABLE_API_PROXY = os.environ.get('CYCLESTREETS_ENABLE_API_PROXY', True) in ("True", True)
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

CORS_ORIGIN_WHITELIST = [
    'http://cyklomapa.plzne.cz',
    'https://cyklomapa.plzne.cz',
]
AKLUB_CORS_ORIGIN_WHITELIST = os.environ.get('AKLUB_CORS_ORIGIN_WHITELIST', None)
if AKLUB_CORS_ORIGIN_WHITELIST:
    CORS_ORIGIN_WHITELIST += AKLUB_CORS_ORIGIN_WHITELIST.split(',')
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
            'filename': os.environ.get('PNK_LOG_FILE', "/var/log/django/pnk.log"),
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

ALLOWED_HOSTS = os.environ.get('AKLUB_ALLOWED_HOSTS', '').split(':')

FEEDBACK_CAPTCHAS = [
    (_("Nejste robot? Napište, kolik kol má obvykle jízdní kolo"), ["2", "dvě", "dve", "dva", "two"]),
]

try:
    RELEASE = raven.fetch_git_sha(PROJECT_DIR)
except raven.exceptions.InvalidGitRepository:
    RELEASE = os.getenv('HEROKU_SLUG_COMMIT')

RAVEN_CONFIG = {
    'dsn': os.environ.get('RAVEN_DNS', ''),
    'release': RELEASE,
}

CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = 60
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
X_FRAME_OPTIONS = 'DENY'

FEEDBACK_CAPTCHAS = [
    (_("Kolik kol má jízdní kolo?"), ["2", "dvě", "dve", "dva", "two"]),
]

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'eu-west-1')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME', 'cyklomapa-test-media')
AWS_QUERYSTRING_AUTH = os.environ.get('AWS_QUERYSTRING_AUTH', True)
AWS_QUERYSTRING_EXPIRE = os.environ.get('AWS_QUERYSTRING_EXPIRE', 60 * 60 * 24 * 365 * 10)
AWS_DEFAULT_ACL = None


if AWS_ACCESS_KEY_ID:
    AWS_SES_REGION_NAME = os.environ.get('AWS_SES_REGION_NAME', 'eu-west-1')
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3-{AWS_SES_REGION_NAME}.amazonaws.com'
    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/"
    DEFAULT_FILE_STORAGE = 'cyklomapa.storage_backends.AwsS3MediaStorage'
    THUMBNAIL_DEFAULT_STORAGE = 'cyklomapa.storage_backends.AwsS3MediaStorage'
    THUMBNAIL_SUBDIR = 'thumbs'

    AWS_SES_REGION_ENDPOINT = 'email.eu-west-1.amazonaws.com'
    EMAIL_BACKEND = 'django_ses.SESBackend'
    MEDIA_ROOT = ""


CYCLESTREETS_API_KEY = os.environ.get('CYCLESTREETS_API_KEY', 'csapi-key-not-set')

DEV_SETTINGS = ('project.settings.dockerdev', 'project.settings.dev')
