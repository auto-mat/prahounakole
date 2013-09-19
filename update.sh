#!/bin/sh

sudo git pull origin master
sudo python manage.py collectstatic --noinput
touch wsgi.py
