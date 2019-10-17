#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from codecs import open  # To use a consistent encoding

from setuptools import setup, find_packages  # Always prefer setuptools over distutils

APP_NAME = 'yoctools'
VERSION = '1.0.11'

settings = dict()


settings.update(
    name=APP_NAME,
    version=VERSION,
    description='YoC tools',
    author='Zhuzhg',
    author_email='zzg@ifnfn.com',
    packages=find_packages(),
    # packages = ['occ'],
    install_requires=['pyyaml>=5.0.0', 'scons>=3.0.0', 'GitPython>=3.0.0'],
    license='BSD',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    entry_points={
        'console_scripts': [
            'yoc = yoctools.yoc:main',
            'csi = yoctools.csi:gen_chip_sdk',
        ],
    }
)


setup(**settings)
