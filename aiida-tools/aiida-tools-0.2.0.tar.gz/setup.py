#!/usr/bin/env python
# -*- coding: utf-8 -*-

# © 2017-2019, ETH Zurich, Institut für Theoretische Physik
# Author: Dominik Gresch <greschd@gmx.ch>


import re
from setuptools import setup

readme = """Helper tools for developing AiiDA plugins."""

# Get the version number
with open('./aiida_tools/__init__.py') as f:
    match_expr = "__version__[^'\"]+(['\"])([^'\"]+)"
    version = re.search(match_expr, f.read()).group(2).strip()


setup(
    name='aiida-tools',
    version=version,
    url='https://aiida-tools.readthedocs.io',
    author='Dominik Gresch',
    author_email='greschd@gmx.ch',
    description=readme,
    install_requires=['aiida-core>=1.0.0<2.0.0', 'fsc.export', 'pyyaml'],
    extras_require={
        ':python_version < "3"': ['singledispatch'],
        'doc': ['sphinx', 'sphinx-rtd-theme'],
    },
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: Unix',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Physics',
        'Development Status :: 3 - Alpha'
    ],
    license='Apache 2.0',
    packages=['aiida_tools']
)
