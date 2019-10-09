# !/usr/bin/env python
# coding: utf-8

from setuptools import find_packages
from setuptools import setup

install_requires = []

setup(
    name='nezha',
    version='0.0.63',
    description="nezha, pysuway's utils",
    packages=find_packages(),
    install_requires=install_requires,
    include_package_data=True
)
