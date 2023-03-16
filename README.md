[![Build Status](https://travis-ci.org/auto-mat/prahounakole.svg?branch=master)](https://travis-ci.org/auto-mat/prahounakole)
[![Coverage Status](https://coveralls.io/repos/github/auto-mat/prahounakole/badge.svg?branch=master)](https://coveralls.io/github/auto-mat/prahounakole?branch=master)

Mapa městem na kole (City map by bike) django app
------------------------------------------------------------

Cycle map of the Django application [City by bike](http://mapa.prahounakole.cz)
developed by the non-profit [Auto*mat](https://www.auto-mat.cz/) organization
in the Czech Republic.

It brings you the best selection of practical cycling routes around the area
Prague. The routes in the cycle map expand the existing network of marked
cycle routes by suitable routes throughout Prague, including the center.
Routes are a selection of secondary ones alleys, park paths, unused sidewalks
and funny shortcuts.

This readme file is intended to document how to develop the code.

City map by bike app is designed to use Python 3.9 and Django 2.28.

Dependencies
------------

 - Docker Engine
 - Docker Compose

Check [docker](https://docs.docker.com/) documentation for installation instructions

Setting up the dev env
===================


Check out and setup repo
------------------------

    $ git clone https://github.com/auto-mat/prahounakole.git
    $ cd prahounakole

Create a .env file
------------------------

    $ cp docker/build-env .env
    $ $EDITOR .env

Building the docker images
--------------------------

    $ docker-compose build

Setting up the database
---------------------

In a separate emulator terminal window:

    $ ./dev/develop.sh
    $ ./dev/setup.sh

Launching the development webserver
------------------------------------

    $ ./dev/develop.sh
    $ python3 manage.py runserver 0.0.0.0:8001


Open the web app
-------------------

Go to `http://localhost:8033/`.

Rebuilding the docker images
--------------------------

Before rebuilding images remove .venv directory symlink:

    $ unlink .venv

Setting up superuser account
---------------------

    $ ./dev/develop.sh
    $ python3 manage.py createsuperuser


Go to `http://localhost:8033/admin`.
