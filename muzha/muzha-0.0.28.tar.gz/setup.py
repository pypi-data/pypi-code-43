# !/usr/bin/env python
# coding: utf-8

from setuptools import find_packages
from setuptools import setup

install_requires = [
    'nezha',
]

setup(
    name='muzha',
    version='0.0.28',
    description="muzha, nezha's brother",
    packages=find_packages(),
    install_requires=install_requires,
    include_package_data=True,
)

