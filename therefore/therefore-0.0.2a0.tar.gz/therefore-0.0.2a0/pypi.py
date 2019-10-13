#!/usr/bin/env python
import os
import sys

from distutils.core import setup
from setuptools.command.install import install
import subprocess

VERSION = '0.0.02-alpha'
NAME = sys.argv[2]
del sys.argv[-1]

setup(
  name = f'{NAME}', # How you named your package folder (MyLib)
  packages = [], # Chose the same as "name"
  version = VERSION, # Start with a small number and increase it with every change you make
  license = f'MIT', # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = f'{NAME}', # Give a short description about your library
  author = f'Matthew Hansen', # Type in your name
  author_email = f'{NAME}@mattian.com', # Type in your E-Mail
  url = f'https://github.com/mattian7741/{NAME}', # Provide either the link to your github or to your website
  download_url = f'https://github.com/mattian7741/{NAME}/archive/v{VERSION}.tar.gz', # github release url
  keywords = [], # Keywords that define your package best
  install_requires=[ # dependencies
  ],
  classifiers=[
    f'Development Status :: 3 - Alpha', # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    f'Intended Audience :: Developers', # Define that your audience are developers
    f'Topic :: Software Development :: Build Tools',
    f'License :: OSI Approved :: MIT License', # Again, pick a license
    f'Programming Language :: Python :: 3', #Specify which pyhton versions that you want to support
    f'Programming Language :: Python :: 3.4',
    f'Programming Language :: Python :: 3.5',
    f'Programming Language :: Python :: 3.6',
  ],
  python_requires='>=3',
)

