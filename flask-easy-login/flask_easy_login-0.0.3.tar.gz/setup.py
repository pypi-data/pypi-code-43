# !/usr/bin/env python
# coding: utf-8

from setuptools import find_packages
from setuptools import setup

install_requires = [
    'flask_requests',
    'flask_simple_token',
    'flask_simple_user'
]

setup(
    name='flask_easy_login',
    version='0.0.3',
    description="flask_login",
    packages=find_packages(),
    install_requires=install_requires,
    include_package_data=True,
)

