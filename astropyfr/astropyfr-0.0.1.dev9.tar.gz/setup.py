#!/usr/bin/env python
# -*- coding: utf-8 -*- 
"""
    This file is part of astro_py
    Author: Stéphane Bressani (s.bressani@bluewin.ch)
"""

from setuptools import setup
from setuptools import find_packages


setup(
    # Project
    name = 'astropyfr',
    version = '0.0.1.dev9',
    
    # Sources
    # packages = ['astro_py'],
    
    package_data = {
        'astropy': ['assets/*.dat']
    #     'flatlib': [
    #         'resources/README.md',
    #         'resources/swefiles/*'
    #     ],
    },
    
    # Sources
    packages = find_packages(),

    # package_data = {
    #     'flatlib': [
    #         'resources/README.md',
    #         'resources/swefiles/*'
    #     ],
    # },
    
    # Dependencies
    install_requires = ['flatlibfr>=0.0.1.dev7'],
    
    # Metadata
    description = 'Python library for Traditional Astrology with export json',
    url = 'https://github.com/stephaneworkspace/astro_py',
    keywords = ['Astrology', 'Traditional Astrology'],
    license = 'GPL',
    
    # Authoring
    author = 'Stéphane Bressani',
    author_email = 's.bressani@bluewin.ch',
    
    # Classifiers
    classifiers = [
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Development Status :: 4 - Beta',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ], 
)
