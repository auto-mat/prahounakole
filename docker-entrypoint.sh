#!/bin/bash
# Add variables into crontab
CRONTAB_FILE=/tmp/crontab
if [ -f $CRONTAB_FILE ]; then rm $CRONTAB_FILE; fi
su test -c 'for i in "DB_USER=$DB_USER" "DB_PASSWORD=$DB_PASSWORD" "DB_NAME=$DB_NAME"; do echo $i >> '$CRONTAB_FILE'; done;'
su test -c "crontab -l >> "$CRONTAB_FILE""
su test -c "crontab "$CRONTAB_FILE""
exec /usr/bin/supervisord --configuration /etc/supervisor/supervisord.conf
