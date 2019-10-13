#!/usr/bin/env python
# -*- coding: utf-8 -*-
from io import open
from setuptools import setup

version = '0.5.2'

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='oweatherm',
    version=version,

    author='nedogimov',
    author_email='mrfoxit01@gmail.com',

    description=(
        u'Weather from OpenWeatherMap'
    ),
    long_description=long_description,
    long_description_content_type='text/markdown',

    license='Apache License, Version 2.0',

    packages=['weather'],
    install_requires=['requests'],

    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Programming Language :: Python :: Implementation :: CPython',
    ]
)
