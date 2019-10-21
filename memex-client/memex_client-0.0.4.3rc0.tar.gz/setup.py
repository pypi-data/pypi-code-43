#!/usr/bin/env python
"""A setuptools based setup module for brainiac"""
# -*- coding: utf-8 -*-

from codecs import open
from os import path
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as readme_file:
    readme = readme_file.read()

with open(path.join(here, 'HISTORY.rst'), encoding='utf-8') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

requirements = [
    # TODO: put package requirements here
    "cloudpickle"
]

test_requirements = [
    # TODO: put package test requirements here
    "cloudpickle"
]

setup(
    name='memex_client',
    version="0.0.4.3-preview",
    description="The client library to make and use brainiac modules.",
    # long_description=readme + '\n\n' + history,
    author="Suyog Soti",
    author_email='suyog.soti@gmail.com',
    url='https://github.com/suyogsoti/client-lib',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    include_package_data=True,
    install_requires=requirements,
    license="MIT",
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.7',
    ],
    test_suite='tests',
    tests_require=test_requirements,
)
