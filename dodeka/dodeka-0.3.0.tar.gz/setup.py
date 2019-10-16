#!/usr/bin/env python3
"""
Copyright (c) 2019, Nils P. Müller <shimst3r@gmail.com>
All rights reserved.

This file is part of dodeka.

License: MIT, see https://opensource.org/licenses/MIT
"""

from setuptools import setup

import m2r

__version__ = "0.3.0"

ENTRY_POINTS = {"console_scripts": ["dodeka = dodeka.interface:dodeka"]}

# The README is written using markdown, PyPI expects the long description
# to be written in reStructuredText. Thus the `m2r` converter is used
# for converting between the two.
with open("README.md", "r", encoding="utf-8") as f_in:
    LONG_DESCRIPTION = m2r.convert(f_in.read())

PACKAGES = ["dodeka"]

REQUIRES = ["Click", "jinja2"]

setup(
    author="Nils P. Müller",
    author_email="shimst3r@gmail.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    description="Twelve-Factor App Checker",
    download_url=f"https://github.com/shimst3r/dodeka/archive/{__version__}.tar.gz",
    entry_points=ENTRY_POINTS,
    install_requires=REQUIRES,
    keywords=["cli", "tool", "twelvefactor"],
    license="MIT",
    long_description=LONG_DESCRIPTION,
    name="dodeka",
    packages=PACKAGES,
    python_requires=">=3.7",
    url="https://github.com/shimst3r/dodeka",
    version=__version__,
)
