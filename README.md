Sorry, no english info at moment. Please contact redakce@prahounakole.cz with any questions.

Mapa Prahou na kole
============

Django aplikace cyklistická mapa Prahou na kole http://mapa.prahounakole.cz

Přináší vám nejkvalitnější výběr praktických tras pro jízdu na kole po Praze. Trasy v cyklomapě rozšiřují stávající síť značených cyklotras o vhodné trasy v celé Praze včetně centra. Trasy tvoří výběr vedlejších uliček, parkových cest, nepoužívaných chodníků a vtipných zkratek.

Instalace
============

Ke zprovoznění je zapotřebí následující

* Virtualenv
* Postgres 8.4 + postgis 1.5

Vzorová lokální konfigurace je v project/settings_local_sample.py, stačí přejmenovat na settings_local.py a doplnit přístup k DB a SECRET_KEY.

Instalace probíhá pomocí následujícíh příkazu:

* ./update.sh reinstall

Spuštění
============

Pro testovací účely spustíte projekt pomocí následujícího příkazu:

* env/bin/python manage.py runserver 0.0.0.0:8000
