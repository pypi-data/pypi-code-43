#!/usr/bin/env python

from setuptools import find_packages, setup

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
  name='packmaker',
  version='0.2.2',
  description='minecraft modpack maker',
  long_description=long_description,
  long_description_content_type="text/markdown",
  author='Mark Crewson',
  author_email='mark@crewson.net',
  url="http://minecraft.pages.routh.io/tools/packmaker",

  classifiers=[
    "Development Status :: 4 - Beta",
    "Environment :: Console",
    "License :: OSI Approved :: Apache Software License",
    "Operating System :: POSIX :: Linux",
    "Topic :: Games/Entertainment",
  ],

  keywords='minecraft modded modpack',

  packages=find_packages(),

  install_requires=[
    'prettytable',
    'python-dateutil',
    'pyyaml',
    'requests',
    'requests_cache',
    'urllib3',
  ],

  python_requires='>=3',

  entry_points={
    'console_scripts': [
        'packmaker = packmaker.main:main'
    ]
  }
)
