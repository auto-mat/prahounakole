FROM python:3.6
RUN curl -sL https://deb.nodesource.com/setup_10.x | bash -
RUN apt-get -qq update; apt-get -y install nodejs gettext libgettextpo-dev libgraphviz-dev libz-dev libjpeg-dev libfreetype6-dev python-dev gdal-bin python-numpy
RUN npm install -g less bower
RUN pip3 install pipenv
RUN useradd test
RUN chsh test -s /bin/bash
RUN mkdir /home/test ; chown test /home/test ; chgrp test /home/test
WORKDIR "/home/test"
copy . .
RUN chown -R test /home/test ; chgrp -R test /home/test
RUN su test ; cd /home/test ; pipenv install --python python3
