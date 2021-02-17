[![Build Status](https://travis-ci.org/auto-mat/prahounakole.svg?branch=master)](https://travis-ci.org/auto-mat/prahounakole)
[![Coverage Status](https://coveralls.io/repos/github/auto-mat/prahounakole/badge.svg?branch=master)](https://coveralls.io/github/auto-mat/prahounakole?branch=master)

Sorry, no english info at moment. Please contact redakce@prahounakole.cz with any questions.

Mapa Prahou na kole
============

Django aplikace cyklistická mapa Prahou na kole http://mapa.prahounakole.cz

Přináší vám nejkvalitnější výběr praktických tras pro jízdu na kole po Praze. Trasy v cyklomapě rozšiřují stávající síť značených cyklotras o vhodné trasy v celé Praze včetně centra. Trasy tvoří výběr vedlejších uliček, parkových cest, nepoužívaných chodníků a vtipných zkratek.

Instalace
============

Ke zprovoznění je zapotřebí následující

* `virtualenv`
* `postgres` a `postgis` novější verze

Může být potřeba vykonat následující příkazy:
```
# nainstalovat závislosti od balíků z requirements
sudo apt install libxml2-dev libxslt1-dev libjpeg-dev postgresql-server-dev

# nainstalovat Bower
sudo apt npm
npm install bower nodejs
npm install -g bower
ln -s /usr/bin/nodejs /usr/bin/node  # pokud Bower říká, že mu chybí node

# nainstalovat Lessc
sudo npm install -g less
```

Nastavení přistupu k databázi:
```
sudo su postgres  # přístup k administraci PostgreSQL
createuser prahounakole  # vytvoření uživatele
createdb prahounakole -O prahounakole  # vytvoření uživatele
psql -c "grant all privileges on database prahounakole to prahounakole;"
psql -c "ALTER USER prahounakole WITH SUPERUSER;"
```

Vzorová lokální konfigurace je v `project/settings_local_sample.py`, stačí přejmenovat na `settings_local.py` a doplnit přístup k databázi (proměnná `DATABASES`) a nastavit proměnnou `SECRET_KEY` na náhodnou hodnotu.

Instalace probíhá pomocí následujícíh příkazu:

* `./update.sh reinstall` (volba `reinstall` zruší `env` a znovu ho nainstaluje, podruhé tedy stačí `./update.sh`)

Spuštění
============

Pro testovací účely spustíte projekt pomocí následujícího příkazu:
```
env/bin/python manage.py runserver 0.0.0.0:8000
```

Installation (Docker compose)
==========================

    $ docker-compose build
    # Or if you want map container user with host user via (ID, GID),
    # default container user 'test' ID=1000, GID=1000
    $ docker-compose build --build-arg USER_ID=$(id -u ${USER}) --build-arg GROUP_ID=$(id -g ${USER})
    $ docker-compose up
    $ docker exec -it --user test prahounakole_web_1 sh -c "/app-v/post_build.sh"

    Check prahounakole web app on the host web browser with URL http://localhost:8033/
