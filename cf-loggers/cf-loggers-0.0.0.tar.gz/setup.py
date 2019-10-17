#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='cf-loggers',
    version='0.0.0',
    description='Logging module that logs data into elasticsearch. Supports async too.',
    author='Ravi Raja Merugu',
    author_email='ravi@invanalabs.ai',
    url='https://github.com/crawlerflow/cf-loggers',
    packages=find_packages(
        exclude=("examples", "tests"),
    ),
    install_requires=[
        'elasticsearch',
        'elasticsearch-async'
    ]

)
