# !/usr/bin/env python
# coding: utf-8

from setuptools import find_packages
from setuptools import setup

install_requires = [
    'celery',
    'jsonschema',
    'nezha==0.0.45',
    'muzha',
    'pandas',
    'pymongo',
    'redis',
    'flower',
    'blinker',
    'gevent',
    'openpyxl',
    'ipython'
]

setup(
    name='blueCup',
    version='0.0.21',
    description="Little blue cup, who do not love?",
    packages=find_packages(),
    install_requires=install_requires,
)
