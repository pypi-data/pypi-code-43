#!/usr/bin/env python
# coding:utf-8
"""将个人封装的公共方法打包"""
from setuptools import setup, find_packages


PACKAGE_NAME = "deng"
PACKAGE_VERSION = "2019.10.16"


setup(
    name=PACKAGE_NAME,
    version=PACKAGE_VERSION,
    description="个人常用方法封装",
    url="https://github.com/Deng2016/deng",
    author="dengqingyong",
    author_email="yu12377@163.com",
    packages=find_packages(),
    exclude_package_data={"": [".gitignore"]},
    install_requires=[
        "requests>=2.18.2",
        "python-dateutil>=1.5",
        "requests-html>=0.9.0",
        ]
)
