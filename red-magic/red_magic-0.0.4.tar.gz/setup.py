#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  7 10:05:18 2019

@author: misiak
"""

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()
    
setuptools.setup(
        name="red_magic",
        version="0.0.4",
        author="Dimitri Misiak",
        author_email="dimitrimisiak@gmail.com",
        description="Generic analysis and processing tools for Manoir.",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://git.ipnl.in2p3.fr/manoir/red_magic",
        packages=setuptools.find_packages(),
        install_requires=[
        	'numpy',
        	'scipy',
        	'matplotlib',
        	'tqdm',
        	'uproot',
        ],
        classifiers=[
                "Programming Language :: Python :: 3",
                "License :: OSI Approved :: MIT License",
                "Operating System :: OS Independent",
        ],
                python_requires=">=3.6",
)



