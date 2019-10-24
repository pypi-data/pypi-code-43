#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup, find_packages
except ImportError:
    import ez_setup
    ez_setup.use_setuptools()
    from setuptools import setup, find_packages

import os

setup(
    name = "django2-piston",
    version = "2.2.3",
    url = 'https://github.com/wilsonchingg/django2-piston',
	download_url = 'https://github.com/wilsonchingg/django2-piston',
    license = 'BSD',
    description = "A Django Piston fork to make it compatible to Django 2 and Python 3",
    author = 'Wilson Ching',
    author_email = 'wilsonchingg96@gmail.com',
    packages = find_packages(),
    namespace_packages = ['piston'],
    include_package_data = True,
    zip_safe = False,
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
