#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

REQUIRES = [
    "numpy",
    "matplotlib",
]
with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='barbatruc',
    version='0.0.2',
    description='Training computational fluid dynamics solver', 
    long_description=readme,
    author='CERFACS-COOP',
    author_email='coop@cerfacs.fr',
    url='https://nitrox.cerfacs.fr/open-source/barbatruc',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'pytest-cov'],
    install_requires=REQUIRES,
)

