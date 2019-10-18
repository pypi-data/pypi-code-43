#!/usr/bin/env python

from setuptools import setup
import setuptools
from dezero import __version__

setup(name='dezero',
      version=__version__,
      license='MIT License',
      install_requires=['numpy'],
      description='deep learning framework from zero',
      author='Koki Saitoh',
      author_email='koki0702@gmail.com',
      url='',
      packages=['dezero'],
     )