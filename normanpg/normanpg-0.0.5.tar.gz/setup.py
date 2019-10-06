#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. currentmodule:: setup.py
.. moduleauthor:: Pat Daburu <pat@daburu.net>

This file is used to create the package we'll publish to PyPI.
"""

import importlib.util
import os
from pathlib import Path
from setuptools import setup, find_packages, Command
from codecs import open  # Use a consistent encoding.
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

# Get the base version from the library.  (We'll find it in the `version.py`
# file in the src directory, but we'll bypass actually loading up the library.)
vspec = importlib.util.spec_from_file_location(
  "version",
  str(Path(__file__).resolve().parent / 'normanpg' / "version.py")
)
vmod = importlib.util.module_from_spec(vspec)
vspec.loader.exec_module(vmod)
version = getattr(vmod, '__version__')

# If the environment has a build number set...
if os.getenv('buildnum') is not None:
    # ...append it to the version.
    version = "{version}.{buildnum}".format(
        version=version,
        buildnum=os.getenv('buildnum')
    )

setup(
    name='normanpg',
    description="This is a set of modest utilities that may be helpful when talking to PostgreSQL.",
    long_description=long_description,
    packages=find_packages(
        exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    version=version,
    install_requires=[
        # Include your dependencies here.
        # Here are a couple of examples...
        # 'numpy>=1.13.3,<2',
        # 'measurement>=1.8.0,<2'
        'click>=7.0,<8',
        'psycopg2-binary>=2.7.4,<3',
        'shapely[vectorized]'
    ],
    entry_points="""
    [console_scripts]
    normanpg=normanpg.cli:cli
    """,
    python_requires=">=0.0.1",
    license='MIT',
    author='Pat Daburu',
    author_email='pat@daburu.net',
    # Use the URL to the github repo.
    url='https://github.com/patdaburu/normanpg',
    download_url=(
        f'https://github.com/patdaburu/'
        f'normanpg/archive/{version}.tar.gz'
    ),
    keywords=[
        # Add package keywords here.
    ],
    # See https://PyPI.python.org/PyPI?%3Aaction=list_classifiers
    classifiers=[
      # How mature is this project? Common values are
      #   3 - Alpha
      #   4 - Beta
      #   5 - Production/Stable
      'Development Status :: 3 - Alpha',

      # Indicate who your project is intended for.
      'Intended Audience :: Developers',
      'Topic :: Software Development :: Libraries',

      # Pick your license.  (It should match "license" above.)
      'License :: OSI Approved :: MIT License',

      # Specify the Python versions you support here. In particular, ensure
      # that you indicate whether you support Python 2, Python 3 or both.
      'Programming Language :: Python :: 3.6',
    ],
    include_package_data=True
)
