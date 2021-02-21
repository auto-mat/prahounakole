FROM python:3.6

ARG USER_ID=1000
ARG GROUP_ID=1000
ENV USER='test'

RUN curl -sL https://deb.nodesource.com/setup_10.x | bash -
RUN apt-get -qq update; apt-get -y install nodejs gettext libgettextpo-dev libgraphviz-dev libz-dev libjpeg-dev libfreetype6-dev python3-dev gdal-bin python-numpy locales locales-all
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

WORKDIR "/app-v"
RUN chown -R $USER_ID:$GROUP_ID /app-v
USER ${USER}
COPY Pipfile.lock Pipfile.lock
COPY Pipfile Pipfile
RUN  pipenv install --dev --python python3
COPY . .

USER root
RUN chown -R $USER_ID:$GROUP_ID .
RUN mkdir -p /var/log/django
RUN chown -R ${USER} /var/log/django

WORKDIR "/home/${USER}"
USER ${USER}
RUN npm install
RUN npm install bower less jshint
RUN npm install uglify-js@2.8.21

WORKDIR "/app-v"
ENTRYPOINT ["./docker-entrypoint.sh"]
