#!/bin/bash

pipenv run python manage.py bower install
pipenv run python manage.py collectstatic --noinput
pipenv run python manage.py collectmedia --noinput
cd bower_components/ol2/build/ && pipenv run python build.py -c none ../../../apps/cyklomapa/static/openstreetmap-pnk ../../../apps/cyklomapa/static/js/OpenLayers.PNK.js
cd /app-v
pipenv run python manage.py compress --force
pipenv run python manage.py migrate
pipenv run python manage.py loaddata apps/cyklomapa/fixtures/*
