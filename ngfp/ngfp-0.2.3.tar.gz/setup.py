#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) Ant <ant@anthive.com>

from os import path
from setuptools import setup, find_packages

from ngfp.version import GetVersion


# read the contents of your README file
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()


__version__ = GetVersion()


setup(
    name="ngfp",
    version=__version__,
    author="Ant",
    author_email="ant@anthive.com",
    description="A puzzle game based upon gfpoken.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://salsa.debian.org/ant-guest/gfpoken-in-python",
    license="Apache-2.0",
    setup_requires=["setuptools >= 40.6.3",
                    "twine >= 1.12.1",
                    "wheel >= 0.32.3"
                    ],
    packages=find_packages(),
    install_requires=["pyglet >= 1.3.0",
                      "pycairo",
                      "pygobject"
                     ],
    provides=["ngfp"],
    include_package_data=True,
    entry_points={
        "console_scripts": ["runngfp = ngfp.ngfp:main"]
                 },
    python_requires=">=3",
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX :: Linux",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Games/Entertainment :: Puzzle Games"
    ],
)
