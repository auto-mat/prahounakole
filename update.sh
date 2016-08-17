#!/bin/bash
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
   rm env -rf
   virtualenv --no-site-packages env --python=python3
fi

git pull


if [ "$1" != "no_virtualenv" ]; then
   echo activate
   source env/bin/activate
fi
pip install --process-dependency-links -r requirements.txt
if [ "$1" != "no_virtualenv" ]; then
   pip install "Django<1.10"
fi
if [ "$1" = "migrate" ]; then
   echo "Backuping db..."
   mkdir -p db_backup
   sudo -u postgres pg_dump -C $db_name > db_backup/`date +"%y%m%d-%H:%M:%S"`-pnk.sql
   echo "Migrating..."
   python ./manage.py migrate
fi

bower install
#compile PNK version of OpenLayers:
(cd apps/cyklomapa/static/bow/openlayers/build/ && python build.py -c none ../../../openstreetmap-pnk ../OpenLayers.PNK.js)

python ./manage.py collectstatic --noinput
python ./manage.py compress_create_manifest --force
python ./manage.py collectstatic --noinput

touch wsgi.py
sudo whoami && sudo /etc/init.d/memcached restart
type supervisorctl && sudo supervisorctl restart $app_name

echo "App succesfully updated"
