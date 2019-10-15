#!python
# -*- coding:utf-8 -*-
from __future__ import print_function
from setuptools import setup, find_packages
import laputa_base

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name="laputa_base",
    version=laputa_base.__version__,
    author="zhiyang.liu",
    author_email="zhiyang.liu.o@nio.com",
    description="laputa base frame",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://git.nevint.com/zhiyang.liu.o/laputa_base.git",
    packages=find_packages(),
    install_requires=[
        'aircv>=1.4.6',
        'allure-pytest>=2.8.6',
        'Appium-Python-Client>=0.34',
        'lxml>=4.2.5',
        'matplotlib>=3.0.2',
        'paramiko>=2.4.2',
        'Pillow>=5.3.0',
        'pytest>=5.2.1',
        'pytest-forked>=1.0.2',
        'pytest-html>=1.19.0',
        'pytest-metadata>=1.7.0',
        'pytest-rerunfailures>=7.0',
        'pytest-xdist>=1.30.0',
        'PyYAML>=5.1.2',
        'requests>=2.20.1',
        'requests-toolbelt>=0.9.1',
        'xlrd>=1.1.0',
        'XlsxWriter>=1.1.8',
        'xlutils>=2.0.0',
        'xlwt>=1.3.0'
        ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
