#!/bin/bash
#version 0.2

set -e

if [ "$1" = "reinstall" ]; then
   rm env -rf
   virtualenv --no-site-packages env
fi

git pull
source env/bin/activate
env/bin/python env/bin/pip install -r requirements.txt --upgrade
if [ "$1" = "migrate" ]; then
   echo "Backuping db..."
   mkdir -p db_backup
   sudo -u postgres pg_dump pnk > db_backup/`date +"%y%m%d-%H:%M:%S"`-pnk.sql
   echo "Migrating..."
   env/bin/python ./manage.py migrate
fi
env/bin/python ./manage.py collectstatic --noinput
touch wsgi.py
