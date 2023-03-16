#!/usr/bin/env bash

# Add variables into crontab
CRONTAB_FILE=/tmp/crontab
APP_DIR=/app-v/
VENV=${APP_DIR}.venv
USER="test"

if [ -f $CRONTAB_FILE ]; then rm $CRONTAB_FILE; fi
su ${USER} -c '
if [ -z $DB_HOST ]
then
     for i in "DB_USER=$DB_USER" "DB_PASSWORD=$DB_PASSWORD" "DB_NAME=$DB_NAME"; do echo $i >> '$CRONTAB_FILE'; done;
else
    for i in "DB_USER=$DB_USER" "DB_PASSWORD=$DB_PASSWORD" "DB_NAME=$DB_NAME" "DB_HOST=$DB_HOST" "DB_PORT=$DB_PORT"; do echo $i >> '$CRONTAB_FILE'; done;
fi;
crontab -l >> '$CRONTAB_FILE'
crontab '$CRONTAB_FILE'
rm '$CRONTAB_FILE'
# Django migrate
cd ${APP_DIR}; pipenv run python3 manage.py migrate';
if [ ! -h $VENV ]; then ln -s /home/${USER}/.venv ${APP_DIR}; fi
su ${USER} -c "pipenv shell"
