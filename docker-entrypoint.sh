#!/bin/bash
pipenv run python3 manage.py migrate
exec /usr/bin/supervisord --configuration /etc/supervisor/supervisord.conf
