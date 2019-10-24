#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import setuptools

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="mysql_lingling",
    version="0.0.6",
    author="Wang Dong",
    author_email="20004604@qq.com",
    description="对 mysql-connector 的二次封装",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/qq20004604/my-pip-package-list/tree/master/mysql_lingling/packaging_tutorial",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'mysql-connector>=2.2.9'
    ]
)
