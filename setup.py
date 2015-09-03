# -*- coding: utf-8 -*-

from os import path

from setuptools import setup

VERSION = (0, 1, 0)
__version__ = VERSION
__versionstr__ = '.'.join(map(str, VERSION))

long_description = ''
try:
    f = open(path.join(path.dirname(__file__), 'README.md'))
    long_description = f.read().strip()
    f.close()
except:
    pass


setup(
    name = 'prahounakole',
    description = "Django aplikace cyklistická mapa Prahou na kole http://mapa.prahounakole.cz/",
    url = "http://github.com/auto-mat/prahounakole",
    long_description = long_description,
    version = __versionstr__,
    author = "Auto*Mat",
    author_email = "redakce@prahounakole.cz",
    license = "BSD",
    packages = ['cyklomapa', 'pnk'],
    classifiers = [
        "Development Status :: 4 - Beta",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
    ],
)
