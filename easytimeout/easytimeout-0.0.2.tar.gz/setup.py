#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name = "easytimeout",
    version = "0.0.2",
    keywords = ("timeout", "easytimeout"),
    description = "Add time limit to excution of your function",
    long_description = "Add time limit to excution of your function",
    license = "Apache Licence",

    url = "https://github.com/binzaq/easytimeout.git",
    author = "bizq",
    author_email = "bin.zaq@foxmail.com",

    py_modules=['easytimeout'],
    include_package_data = True,
    platforms = "any",
    install_requires = []
)
