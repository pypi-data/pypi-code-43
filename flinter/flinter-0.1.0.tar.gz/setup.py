#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.md') as f:
    README = f.read()

setup(
    name='flinter',
    version='0.1.0',
    description='Flinter a fortran code linter',
    long_description=README,
    author='CoopTeam-CERFACS',
    author_email='coop@cerfacs.com',
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    entry_points={
        "console_scripts": [
            "flint = flint.linter:main",
            ]
    },
    license="CeCILL-B FREE SOFTWARE LICENSE AGREEMENT",
    url='http://open-source.pg.cerfacs.fr/flint',
    packages=find_packages(exclude=('tests', 'docs')),
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    install_requires=["pyaml"]


)
