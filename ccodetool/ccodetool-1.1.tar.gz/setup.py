#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/10/21 17:31
# @Author  : yuqiang
# @Function: setup.py
# @File    : setup.py.py

from setuptools import setup


setup(

    name='ccodetool',
    version='1.1',
    packages=['ccodetool'],
    zip_safe=True,
    include_package_data=True,
    install_requires=[
    ],
    setup_requires=["pytest-runner"],

)

