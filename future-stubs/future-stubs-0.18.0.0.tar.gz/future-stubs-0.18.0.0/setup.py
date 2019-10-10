#!/usr/bin/env python

from __future__ import absolute_import, print_function

from setuptools import setup


NAME = "future-stubs"
PACKAGES = ['future', 'past']
VERSION = "0.18.0.0"
DESCRIPTION = "PEP 561 stubs for python-future"
AUTHOR = "Chad Dombrova"
AUTHOR_EMAIL = "chadrik@gmail.com"
URL = "https://python-future.org"
LICENSE = "MIT"
KEYWORDS = "future past python3 migration futurize backport six 2to3 modernize pasteurize 3to2 stubs mypy"
CLASSIFIERS = [
    "Programming Language :: Python",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 2.6",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.3",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "License :: OSI Approved",
    "License :: OSI Approved :: MIT License",
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
]

setup(name=NAME,
      version=VERSION,
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      url=URL,
      description=DESCRIPTION,
      license=LICENSE,
      keywords=KEYWORDS,
      package_dir={'': 'src'},
      packages=PACKAGES,
      install_requires=['python-future>=0.16.0'],
      include_package_data=True,
      python_requires=">=2.6, !=3.0.*, !=3.1.*, !=3.2.*",
      classifiers=CLASSIFIERS,
     )
