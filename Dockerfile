FROM python:3.6
RUN curl -sL https://deb.nodesource.com/setup_10.x | bash -
RUN apt-get -qq update; apt-get -y install nodejs gettext libgettextpo-dev libgraphviz-dev libz-dev libjpeg-dev libfreetype6-dev python-dev gdal-bin python-numpy
RUN npm install -g bower less jshint
RUN pip3 install pipenv --upgrade

run mkdir /home/aplikace -p
WORKDIR "/home/aplikace"
copy Pipfile /home/aplikace/Pipfile
copy Pipfile.lock /home/aplikace/Pipfile.lock

RUN pipenv install --ignore-pipfile --verbose

copy . .

RUN pipenv run python ./manage.py bower install
RUN (cd bower_components/ol2/build/ && pipenv run python build.py -c none ../../../apps/cyklomapa/static/openstreetmap-pnk ../../../apps/cyklomapa/static/js/OpenLayers.PNK.js)

RUN pipenv run python ./manage.py collectstatic --noinput
RUN pipenv run python ./manage.py compress_create_manifest --force
RUN pipenv run python ./manage.py collectstatic --noinput
RUN useradd test
RUN chsh test -s /bin/bash
RUN mkdir /home/test ; chown test /home/test ; chgrp test /home/test
RUN su test ; cd /home/test ; pipenv install --dev --python python3

EXPOSE 8000
RUN mkdir media logs -p
VOLUME ["logs", "media"]
ENTRYPOINT ["./docker-entrypoint.sh"]
