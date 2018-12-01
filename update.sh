#!/bin/bash -x
#version 0.3

app_name=pnk
db_name=pnk

error() {
   printf '\E[31m'; echo "$@"; printf '\E[0m'
}

if [[ $EUID -eq 0 ]]; then
   error "This script should not be run using sudo or as the root user"
   exit 1
fi

source update_local.sh

set -e

if [ "$1" = "reinstall" ]; then
   pipenv --rm
fi

pipenv install --python=python3

if [ "$1" != "no_virtualenv" ]; then
   pipenv install "Django<3.0" --upgrade
fi
if [ "$1" = "migrate" ]; then
   echo "Backuping db..."
   mkdir -p db_backup
   sudo -u postgres pg_dump -C $db_name > db_backup/`date +"%y%m%d-%H:%M:%S"`-pnk.sql
   echo "Migrating..."
   pipenv run python ./manage.py migrate
fi

pipenv run python ./manage.py bower install
#compile PNK version of OpenLayers:
(cd bower_components/ol2/build/ && pipenv run python build.py -c none ../../../apps/cyklomapa/static/openstreetmap-pnk ../../../apps/cyklomapa/static/js/OpenLayers.PNK.js)

pipenv run python ./manage.py collectstatic --noinput
pipenv run python ./manage.py compress_create_manifest --force
pipenv run python ./manage.py collectstatic --noinput

touch wsgi.py
sudo whoami && sudo /etc/init.d/memcached restart
type supervisorctl && sudo supervisorctl restart $app_name

echo "App succesfully updated"
