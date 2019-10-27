#!/usr/bin/python
# -*- coding: utf-8 -*-


from setuptools import find_packages, setup

setup (
    name = 'satup',
    version = '0.1.0',
    author = 'Tomaszek',
    author_email = 'czornytomaszek@gmail.com',
    pachages=find_packages(),
    include_package_data=True,
    description='Super useful library'
)