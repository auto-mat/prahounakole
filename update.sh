#!/bin/sh

sudo git pull origin master
sudo env/bin/python manage.py collectstatic --noinput
touch wsgi.py
