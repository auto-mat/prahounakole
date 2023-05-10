FROM python:3.9-bullseye

ARG USER_ID=1000
ARG GROUP_ID=1000
ENV USER='test'
ENV PATH=$PATH:/home/$USER/.local/bin

RUN DISTRIBUTION_CODENAME=$(cat /etc/os-release | grep VERSION_CODENAME | cut -d "=" -f 2); NON_FREE_REPOSITORY="deb http://deb.debian.org/debian ${DISTRIBUTION_CODENAME} non-free\n\
deb-src http://deb.debian.org/debian ${DISTRIBUTION_CODENAME} non-free\n\
deb http://deb.debian.org/debian-security/ ${DISTRIBUTION_CODENAME}-security non-free\n\
deb-src http://deb.debian.org/debian-security/ ${DISTRIBUTION_CODENAME}-security non-free\n\
deb http://deb.debian.org/debian ${DISTRIBUTION_CODENAME}-updates non-free\n\
deb-src http://deb.debian.org/debian ${DISTRIBUTION_CODENAME}-updates non-free"; printf "$NON_FREE_REPOSITORY" > /etc/apt/sources.list.d/${DISTRIBUTION_CODENAME}.non-free.list

RUN curl -sL https://deb.nodesource.com/setup_14.x | bash -
RUN apt-get -qq update; apt-get -y install nodejs gettext libgettextpo-dev libgraphviz-dev libz-dev libjpeg-dev libfreetype6-dev python3-dev gdal-bin libgdal-dev python3-numpy locales locales-all cron jq supervisor unrar gawk
ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8
RUN npm install -g less bower

RUN if getent group ${USER}; then groupdel "${USER}"; fi && \
    groupadd --gid "$GROUP_ID" "${USER}" && \
    if getent passwd ${USER}; then userdel -f ${USER}; fi && \
    useradd \
      --uid $USER_ID \
      --gid $GROUP_ID \
      --create-home \
      --shell /bin/bash \
      ${USER}

USER ${USER}
RUN pip3 install --disable-pip-version-check --no-warn-script-location --user pipenv
USER root

WORKDIR "/home/${USER}"
RUN mkdir /app-v; chown -R $USER_ID:$GROUP_ID /app-v
USER ${USER}
COPY --chown=$USER_ID:$GROUP_ID Pipfile.lock Pipfile.lock
COPY --chown=$USER_ID:$GROUP_ID Pipfile Pipfile
RUN CPLUS_INCLUDE_PATH=/usr/include/gdal C_INCLUDE_PATH=/usr/include/gdal PIPENV_VENV_IN_PROJECT=True pipenv install --dev --python python3
COPY --chown=$USER_ID:$GROUP_ID . .
COPY --chown=$USER_ID:$GROUP_ID ./docker/build-env ./.env

USER root
RUN mkdir -p /var/log/django/cron
RUN chown -R ${USER} /var/log/django
RUN service cron start

USER ${USER}
RUN npm install
RUN npm install bower less jshint
RUN npm install uglify-js@2.8.21
RUN pipenv run python3 manage.py bower install
RUN pipenv run python3 manage.py collectstatic --noinput
RUN pipenv run python3 manage.py collectmedia --noinput
RUN cd bower_components/ol2/build/ && pipenv run python3 build.py -c none ../../../apps/cyklomapa/static/openstreetmap-pnk ../../../apps/cyklomapa/static/js/OpenLayers.PNK.js
RUN pipenv run python3 manage.py compress
RUN pipenv run python3 manage.py crontab add
# RUN DOWNLOAD_CYKLISTESOBE_TRACKS_JOB_ID=$(pipenv run python3 manage.py crontab show | sed -n '2,$p' | awk -F ", " '{if(match($2, "download_cyklistesobe_tracks") > 0) print $1}' | awk -F " -> " '{print $1}'); $(crontab -l | sed -n
# "/${DOWNLOAD_CYKLISTESOBE_TRACKS_JOB_ID}/p" | cut -f 6- -d ' ' | sed 's/# django-cronjobs for project//g')
RUN pipenv run python3 manage.py downloadcyklistesobelayer --task download_only
RUN rm .env

USER root
RUN mkdir -p /var/log/supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

ENTRYPOINT ["./docker-entrypoint.sh"]
