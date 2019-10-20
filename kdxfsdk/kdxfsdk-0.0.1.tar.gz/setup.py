#!/usr/bin/env python
#-*- coding:utf-8 -*-

#############################################
#  File Name: setup.py
#  Author: xialingming
#  Mail: xialingming@gmail.com
#  #############################################


from setuptools import setup, find_packages

setup(
    name="kdxfsdk",
    version="0.0.1",
    keywords=("kdxf", "sdk", "xialingming"),
    description="kdxf sdk",
    long_description="xf sdk for python",
    license="MIT Licence",

    url="http://xialingming",
    author="lmxia",
    author_email="xialingming@gmail.com",

    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    install_requires=["requests"]
)