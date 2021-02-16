FROM python:3.6

ARG USER_ID
ARG GROUP_ID
ENV USER='test'
ENV DEF_USER_ID=1000
ENV DEF_GROUP_ID=1000

RUN curl -sL https://deb.nodesource.com/setup_10.x | bash -
RUN apt-get -qq update; apt-get -y install nodejs gettext libgettextpo-dev libgraphviz-dev libz-dev libjpeg-dev libfreetype6-dev python3-dev gdal-bin python-numpy locales locales-all
RUN npm install -g less bower
RUN pip3 install pipenv

RUN if getent group ${USER}; then groupdel "${USER}"; fi && \
    groupadd --gid "${GROUP_ID:-${DEF_GROUP_ID}}" "${USER}" && \
    if getent passwd ${USER}; then userdel -f ${USER}; fi && \
    useradd \
      --uid ${USER_ID:-${DEF_USER_ID}} \
      --gid ${GROUP_ID:-${DEF_GROUP_ID}} \
      --create-home \
      --shell /bin/bash \
      ${USER}

WORKDIR "/app-v"
RUN chown -R ${USER_ID:-${DEF_USER_ID}}:${GROUP_ID:-${DEF_GROUP_ID}} /app-v
USER ${USER}
COPY --chown=${USER_ID:-${DEF_USER_ID}}:${GROUP_ID:-${DEF_GROUP_ID}} Pipfile.lock Pipfile.lock
COPY --chown=${USER_ID:-${DEF_USER_ID}}:${GROUP_ID:-${DEF_GROUP_ID}} Pipfile Pipfile
RUN pipenv install --dev --python python3
COPY --chown=${USER_ID:-${DEF_USER_ID}}:${GROUP_ID:-${DEF_GROUP_ID}} . .
COPY --chown=${USER_ID:-${DEF_USER_ID}}:${GROUP_ID:-${DEF_GROUP_ID}} ./docker/build-env ./.env

USER root
RUN rm -rf /app-v
RUN mkdir -p /var/log/django
RUN chown -R ${USER} /var/log/django

WORKDIR "/home/${USER}"
USER ${USER}
RUN npm install
RUN npm install bower less jshint
RUN npm install uglify-js@2.8.21

ENTRYPOINT ["./docker-entrypoint.sh"]
