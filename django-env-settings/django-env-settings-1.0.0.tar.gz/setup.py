#!/usr/bin/env python3
from setuptools import setup


setup(
    name='django-env-settings',
    version='1.0.0',
    author='Victor',
    author_email='victor@what.digital',
    url='https://gitlab.com/what-digital/django-env-settings',
    packages=[
        'env_settings',
    ],
    include_package_data=True,
    install_requires=[
        'django >= 2.1, < 3',
    ],
)
