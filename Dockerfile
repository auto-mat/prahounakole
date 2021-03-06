FROM python:3.6

ARG USER_ID=1000
ARG GROUP_ID=1000
ENV USER='test'

RUN curl -sL https://deb.nodesource.com/setup_10.x | bash -
RUN apt-get -qq update; apt-get -y install nodejs gettext libgettextpo-dev libgraphviz-dev libz-dev libjpeg-dev libfreetype6-dev python3-dev gdal-bin libgdal-dev python-numpy locales locales-all cron jq supervisor
ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8
RUN npm install -g less bower
RUN pip3 install pipenv

RUN if getent group ${USER}; then groupdel "${USER}"; fi && \
    groupadd --gid "$GROUP_ID" "${USER}" && \
    if getent passwd ${USER}; then userdel -f ${USER}; fi && \
    useradd \
      --uid $USER_ID \
      --gid $GROUP_ID \
      --create-home \
      --shell /bin/bash \
      ${USER}

WORKDIR "/home/${USER}"
RUN mkdir /app-v; chown -R $USER_ID:$GROUP_ID /app-v
USER ${USER}
COPY Pipfile.lock Pipfile.lock
COPY Pipfile Pipfile
RUN CPLUS_INCLUDE_PATH=/usr/include/gdal C_INCLUDE_PATH=/usr/include/gdal pipenv install --dev --python python3
COPY . .
COPY ./docker/build-env ./.env

USER root
RUN chown -R $USER_ID:$GROUP_ID .
RUN mkdir -p /var/log/django
RUN chown -R ${USER} /var/log/django
RUN service cron start

USER ${USER}
RUN npm install
RUN npm install bower less jshint
RUN npm install uglify-js@2.8.21
RUN pipenv run python3 manage.py bower install
RUN pipenv run python3 manage.py collectstatic --noinput
RUN pipenv run python manage.py collectmedia --noinput
RUN cd bower_components/ol2/build/ && pipenv run python build.py -c none ../../../apps/cyklomapa/static/openstreetmap-pnk ../../../apps/cyklomapa/static/js/OpenLayers.PNK.js
RUN pipenv run python3 manage.py compress
RUN pipenv run python3 manage.py crontab add
RUN $(crontab -l | cut -f 6- -d ' ' | sed 's/# django-cronjobs for project//g')

USER root
RUN mkdir -p /var/log/supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

ENTRYPOINT ["./docker-entrypoint.sh"]