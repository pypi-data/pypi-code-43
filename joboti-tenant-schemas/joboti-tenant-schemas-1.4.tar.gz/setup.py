#!/usr/bin/env python

from os.path import exists

from version import get_git_version

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='joboti-tenant-schemas',
    version='1.4',
    author='Ilyes Ahmed Hammadi',
    author_email='hammadiilyesahmed@gmail.com',
    packages=[
        'tenant_schemas',
        'tenant_schemas.migration_executors',
        'tenant_schemas.postgresql_backend',
        'tenant_schemas.management',
        'tenant_schemas.management.commands',
        'tenant_schemas.templatetags',
        'tenant_schemas.test',
        'tenant_schemas.tests',
    ],
    scripts=[],
    url='https://github.com/joboti-com/django-tenant-schemas',
    license='MIT',
    description='Remove postgis as original backend and added search_set support',
    long_description=open('README.rst').read() if exists("README.rst") else "",
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Programming Language :: Python',
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
        "Topic :: Database",
        "Topic :: Software Development :: Libraries",
    ],
    install_requires=[
        'Django',
        'psycopg2-binary',
    ],
    zip_safe=False,
)
