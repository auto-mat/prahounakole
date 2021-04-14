#!/bin/bash
# Add variables into crontab
CRONTAB_FILE=/tmp/crontab
if [ -f $CRONTAB_FILE ]; then rm $CRONTAB_FILE; fi
su test -c '
for i in "DB_USER=$DB_USER" "DB_PASSWORD=$DB_PASSWORD" "DB_NAME=$DB_NAME" "DB_HOST=$DB_HOST" "DB_PORT=$DB_PORT"; do echo $i >> '$CRONTAB_FILE'; done;
crontab -l >> '$CRONTAB_FILE'
crontab '$CRONTAB_FILE'
rm '$CRONTAB_FILE''
# Django migrate
su test -c "cd /home/test; pipenv run python3 manage.py migrate"
# Run supervisord
exec /usr/bin/supervisord --configuration /etc/supervisor/supervisord.conf
