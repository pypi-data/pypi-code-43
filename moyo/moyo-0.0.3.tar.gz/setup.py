#!/usr/bin/env python
# coding=utf-8

from setuptools import setup, find_packages

setup(
    name='moyo',
    version='0.0.3',
    description='A high performance API server, support REST style',
    long_description='A high performance API server, support REST style',
    author='bxy',
    author_email='chdhyc@foxmail.com',
    maintainer='bxy',
    maintainer_email='chdhyc@foxmail.com',
    license='BSD License',
    packages=find_packages(),
    platforms="any",
    url='https://www.baidu.com',
    install_requires=[
        'gevent',
    ]
)
