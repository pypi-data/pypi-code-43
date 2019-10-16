#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def get_version(*file_paths):
    """Retrieves the version from pwny/__init__.py"""
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    version_file = open(filename).read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


version = get_version("pwny", "__init__.py")

readme = open("README.rst").read()

setup(
    name="django-pwny",
    version=version,
    description="""Have I Been Pwned? password validator""",
    long_description=readme,
    author="PsypherPunk",
    author_email="psypherpunk@gmail.com",
    url="https://github.com/PsypherPunk/django-pwny",
    packages=["pwny"],
    include_package_data=True,
    install_requires=[],
    license="Apache Software License 2.0",
    zip_safe=False,
    keywords="django-pwny",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Django :: 1.11",
        "Framework :: Django :: 2.0",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)
