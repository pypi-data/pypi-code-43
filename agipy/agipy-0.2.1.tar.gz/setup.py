#!/usr/bin/env python3

"""
agipy enables you to destroy cloud infrastructure in a hurry.
Copyright (C) 2019  Nils Müller <shimst3r@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>
"""


from setuptools import setup

import m2r

__version__ = "0.2.1"

ENTRY_POINTS = {"console_scripts": ["agipy = agipy.agipy:interface"]}

# The README is written using markdown, PyPI expects the long description
# to be written in reStructuredText. Thus the `m2r` converter is used
# for converting between the two.
with open("README.md", "r", encoding="utf-8") as f_in:
    LONG_DESCRIPTION = m2r.convert(f_in.read())

PACKAGES = ["agipy", "agipy.providers"]

REQUIRES = {
    "azure": ["azure-common", "azure-mgmt-resource", "msrestazure"],
    "general": ["Click"],
}

setup(
    author="Nils P. Müller",
    author_email="shimst3r@gmail.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    description="destroy cloud infrastructure in a hurry",
    download_url=f"https://github.com/shimst3r/agipy/archive/{__version__}.tar.gz",
    entry_points=ENTRY_POINTS,
    install_requires=[package for section in REQUIRES.values() for package in section],
    keywords=["azure", "cli", "cloud", "devops", "sysadmin", "tool"],
    license="GPL",
    long_description=LONG_DESCRIPTION,
    name="agipy",
    packages=PACKAGES,
    python_requires=">=3.7",
    url="https://github.com/shimst3r/agipy",
    version=__version__,
)
