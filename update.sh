#!/bin/sh

sudo git pull origin master
env/bin/pip install -r requirements.txt
sudo env/bin/python manage.py dumpdata > db_backup/`date +"%y%m%d"`-mapa.json
sudo env/bin/python manage.py migrate
sudo env/bin/python manage.py collectstatic --noinput
touch wsgi.py
sudo /etc/init.d/memcached restart
