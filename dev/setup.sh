#!/usr/bin/env bash

pipenv run python3 manage.py bower install
pipenv run python3 manage.py collectstatic --noinput
pipenv run python3 manage.py collectmedia --noinput
cd bower_components/ol2/build/ \
    && python3 build.py -c none ../../../apps/cyklomapa/static/openstreetmap-pnk ../../../apps/cyklomapa/static/js/OpenLayers.PNK.js \
    && cd /app-v
pipenv run python3 manage.py migrate
pipenv run python3 manage.py loaddata apps/cyklomapa/fixtures/*
