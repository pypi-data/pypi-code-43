#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('VERSION.txt', 'r') as v:
    version = v.read().strip()

with open('README.rst', 'r') as r:
    readme = r.read()

download_url = (
    'https://github.com/jerinpetergeorge/django-model-admin-autocomplete/tarball/%s'
)

setup(
    name='django-model-admin-autocomplete',
    packages=['model_admin_autocomplete'],
    version=version,
    description='Tweaks for existing built-in Django"s autocomplete feature',
    long_description=readme,
    author='Jerin Peter George',
    author_email='jerinpetergeorge@gmail.com',
    url='https://github.com/jerinpetergeorge/django-model-admin-autocomplete',
    download_url=download_url % version,
    install_requires=[],
    license='MIT-Zero'
)
