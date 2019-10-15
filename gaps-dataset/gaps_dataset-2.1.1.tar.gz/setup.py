# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import os
from setuptools import setup, find_packages


def run_setup():
    # get version
    version_namespace = {}
    with open(os.path.join('gaps_dataset', 'version.py')) as version_file:
        exec(version_file.read(), version_namespace)
    version = version_namespace['_get_version'](with_suffix=False)

    # setup
    setup(name='gaps_dataset',
          version='{}.{}.{}'.format(*version),
          description='Download script for GAPs deep learning dataset from TU Ilmenau',
          url='http://www.tu-ilmenau.de/neurob/data-sets-code/gaps/',
          author='Markus Eisenbach',
          author_email='markus.eisenbach@tu-ilmenau.de',
          license=('Copyright 2017, Neuroinformatics and Cognitive Robotics '
                   'Lab TU Ilmenau, Ilmenau, Germany (for academic use only)'),
          install_requires=[
              'numpy'
          ],
          packages=find_packages(),
          extras_require={
              'test': [
                  'pytest>=3.0.2'
              ]
          },
          zip_safe=False)


if __name__ == '__main__':
    run_setup()
