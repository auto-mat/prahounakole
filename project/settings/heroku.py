import os

import django_heroku

from .base import *  # noqa

if 'SENDGRID_USERNAME' in os.environ:
    EMAIL_HOST_USER = os.environ['SENDGRID_USERNAME']
    EMAIL_HOST = 'smtp.sendgrid.net'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_PASSWORD = os.environ['SENDGRID_PASSWORD']

django_heroku.settings(locals())
