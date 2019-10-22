#!/usr/bin/env python3
#     _        _   _ _ _ _
#    / \   ___| |_(_) (_) |_ _   _
#   / _ \ / __| __| | | | __| | | |
#  / ___ \ (__| |_| | | | |_| |_| |
# /_/   \_\___|\__|_|_|_|\__|\__, |
#                            |___/
# Copyright (C) 2019 Actility, SA. All Rights Reserved.
# DO NOT ALTER OR REMOVE COPYRIGHT NOTICES OR THIS FILE HEADER
# License: Revised BSD License, see LICENSE.TXT file included in the project
# author: <raphael.apfeldorfer@actility.com>
# date: Tue September 30 14:45:48 CET 2019

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyThingPark",
    version="0.0.4",
    author="Raphael Apfeldorfer",
    author_email="raphael.apfeldorfer@actility.com",
    description="Python tools for ThingPark",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/actility/pyThingPark",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
    ],
    install_requires=['cryptography'],
    python_requires='>=3.6',
)