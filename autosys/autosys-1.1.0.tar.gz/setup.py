#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import

from setuptools import setup

import autosys

setup(
    name=autosys.name,
    version=autosys.__version__,
    description="System utilities for Python on macOS",
    long_description=open("README.md").read(),
    author="Michael Treanor",
    author_email="skeptycal@gmail.com",
    maintainer="Michael Treanor",
    maintainer_email="skeptycal@gmail.com",
    url="http://github.com/skeptycal/autosys/",
    license="MIT",
    packages=["autosys"],
    install_requires=[],
    test_requore=["tox", "pytest", "coverage", "pytest-cov"],
    test_suite="test",
    zip_safe=False,
    keywords="cli utilities python ai ml text console log debug test testing",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Environment :: MacOS X",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Flask",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: MacOS",
        "Programming Language :: Cython",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Testing",
        "Topic :: Utilities",
    ],
)
