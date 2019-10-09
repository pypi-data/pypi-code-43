#!/usr/bin/env python
# -*- coding: utf-8 -*-
from os import path, environ
from setuptools import setup, find_packages

def read_long_description():
    this_directory = path.abspath(path.dirname(__file__))
    with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()
        return long_description
    

setup(
    name='epylog',
    version='0.1.%s' % environ.get('TRAVIS_BUILD_NUMBER', 0),
    description="Just another one Python logging package.",
    long_description=read_long_description(),
    long_description_content_type='text/markdown',
    keywords='logging',
    author='Alexey Morozov',
    author_email='iphosgen@gmail.com',
    url='https://github.com/iPhosgen/epylog',
    license='MIT License',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: System :: Logging',
    ]
)
