#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from service_runner import version

setup(
    name='service_runner',
    version=version,
    url='https://github.com/wuyue92tree/service_runner',
    description='service manager',
    long_description=open('README.rst').read(),
    author='wuyue',
    author_email='wuyue92tree@163.com',
    maintainer='wuyue',
    maintainer_email='wuyue92tree@163.com',
    license='Apache License 2.0',
    packages=find_packages(exclude=('tests', 'tests.*')),
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': ['service_runner = service_runner.manage:main']
    },
    install_requires=[
        'Django==2.2.6',
        'django-adminlte-ui==1.4.0',
        'ansible==2.7.13',
        'paramiko==2.6.0',
        'channels==2.3.0',
        'kombu==4.6.5',
        'celery==4.3.0',
        'django-celery-beat==1.5.0'
    ],
)
