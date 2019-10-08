#!/usr/bin/env python

from setuptools import setup

with open('README.md', 'r') as fh: long_description = fh.read()

setup(
  name = 'YealinkManager',
  python_requires = '>3.6.0',
  author = 'Giacomo Giusti',
  version = '2.1',
  install_requires=['requests'],
  packages = [ 'yealinkManager' ],
  description = 'Automate Action Uri in yealinkPhone',
  author_email = 'giacomino.giusti@gmail.com',
  entry_points = {
    'console_scripts': [ 
      'ym = yealinkManager.YealinkManager:entryPoint',
      'YealinkManager = yealinkManager.YealinkManager:entryPoint',
    ]
  },
  long_description = long_description,
  long_description_content_type = 'text/markdown',
)  