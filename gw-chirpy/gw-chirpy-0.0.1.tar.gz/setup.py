#!/usr/bin/env python

from distutils.core import setup
from setuptools import find_packages


# https://stackoverflow.com/questions/26900328/install-dependencies-from-setup-py
import os
thelibFolder = os.path.dirname(os.path.realpath(__file__))
requirementPath = thelibFolder + '/requirements.txt'
install_requires = [] # Examples: ["gunicorn", "docutils>=0.3", "lxml==0.5a7"]
if os.path.isfile(requirementPath):
    with open(requirementPath) as f:
        install_requires = f.read().splitlines()

setup(name='gw-chirpy',
      version='0.0.1',
      description='Gravitational Waveforms in python',
      author='Sebastian Khan',
      author_email='sebastian.khan@LIGO.org',
      packages=find_packages(),
      install_requires=install_requires,
      url='https://gitlab.com/SpaceTimeKhantinuum/chirpy'
     )
