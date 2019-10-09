#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec  4 16:39:38 2018

@author: stephan
"""

from setuptools import setup,  find_packages
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.rst'), encoding='utf-8') as f:
    long_descriptions = f.read()

setup(name="SimPel",
      version="1.0.3a",
      author="Stephan Rein",
      author_email="stephan.rein@physchem.uni-freiburg.de",
      url="https://www.radicals.uni-freiburg.de/de/software/simpel",
      packages = find_packages(),
      description='Simulation of PELDOR time traces',
      long_description=long_descriptions,
      long_description_content_type='text/x-rst',
      include_package_data=True,
      package_data={'SimPel': ['*.png', '*.ico', '*.jpg']},
      license="GPLv3",
      keywords=[
        'EPR simulations',
        'DEER',
        'PELDOR',
        'Dipolar spectroscopy',
      ],
      classifiers=[
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Physics'
       ],
      install_requires=[
        'numpy>=1.15.4',
        'PyQt5>=5.11.3',
        'PyQt5-sip>=4.19.13',
	    'numpydoc>=0.9.1',
        'scipy==1.2.0',
        'matplotlib>=3.0.2',
      ],
      python_requires='>=3.5',
      entry_points={
        "gui_scripts": [
        "SimPel = SimPel.SimPel:run",
	    "simpel = SimPel.SimPel:run",
        ]
    })

