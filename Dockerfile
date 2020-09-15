FROM python:3.6
RUN curl -sL https://deb.nodesource.com/setup_10.x | bash -
RUN apt-get -qq update; apt-get -y install nodejs gettext libgettextpo-dev libgraphviz-dev libz-dev libjpeg-dev libfreetype6-dev python3-dev gdal-bin python-numpy locales locales-all
ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8
RUN npm install -g less bower
RUN pip3 install pipenv
RUN useradd test
RUN chsh test -s /bin/bash
RUN mkdir /home/test ; chown test /home/test ; chgrp test /home/test
WORKDIR "/home/test"
copy Pipfile.lock Pipfile.lock
copy Pipfile Pipfile
RUN su test -c 'cd /home/test ; pipenv install --python python3'
copy . .
copy ./docker/build-env ./.env
RUN chown -R test /home/test ; chgrp -R test /home/test
run mkdir -p /var/log/django
run chown -R test /var/log/django
user test
run cd /home/test ; npm install
run cd /home/test ; npm install bower less jshint
run cd /home/test ; npm install uglify-js@2.8.21
run cd /home/test ; pipenv run python3 manage.py bower install
run cd /home/test ; pipenv run python3 manage.py collectstatic --noinput
run cd /home/test ; pipenv run python manage.py collectmedia --noinput
run cd bower_components/ol2/build/ && pipenv run python build.py -c none ../../../apps/cyklomapa/static/openstreetmap-pnk ../../../apps/cyklomapa/static/js/OpenLayers.PNK.js
run cd /home/test ; pipenv run python3 manage.py compress
ENTRYPOINT ["./docker-entrypoint.sh"]