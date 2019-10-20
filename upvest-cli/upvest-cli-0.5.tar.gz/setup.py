# -*- coding: utf-8 -*-
# pylint: skip-file
import codecs
import os
import sys
from distutils.core import setup

from setuptools import find_packages

if sys.version_info < (3, 6):
    raise Exception("Upvest CLI requires Python 3.6 or higher.")

with open("upvest_cli/__pkginfo__.py") as f:
    exec(f.read())
_VERSION = globals()["__version__"]

_PACKAGES = find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"])

_INSTALL_REQUIRES = ["upvest>=0.0.7", "PyYAML>=5.1"]
_OPTIONAL = {"dev": ["pre-commit==1.10.5", "prospector==1.1.6.2"]}

_CLASSIFIERS = [
    "Development Status :: 3 - Alpha",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "Operating System :: OS Independent",
    "Topic :: Software Development",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "License :: OSI Approved :: MIT License",
]

if os.path.exists("README.rst"):
    _LONG_DESCRIPTION = codecs.open("README.rst", "r", "utf-8").read()
else:
    _LONG_DESCRIPTION = ("Upvest CLI: CLI for using the Upvest API. See https://docs.upvest.co",)


setup(
    name="upvest-cli",
    version=_VERSION,
    url="https://docs.upvest.co",
    author="upvest.co",
    author_email="tech@upvest.co",
    license="MIT",
    zip_safe=False,
    description="Upvest CLI: CLI for using the Upvest CLI",
    long_description=_LONG_DESCRIPTION,
    keywords="upvest blockchain api cli",
    classifiers=_CLASSIFIERS,
    packages=_PACKAGES,
    entry_points={"console_scripts": ["upvest = upvest_cli.execute:main"]},
    install_requires=_INSTALL_REQUIRES,
    extras_require=_OPTIONAL,
)
