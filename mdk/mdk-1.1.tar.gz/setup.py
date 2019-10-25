#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
"""build/set up mdk"""
from setuptools import find_packages
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    author='Michael Darr',
    author_email='mdarr@matician.com',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ],
    description='a docker-compose helper',
    entry_points={
        'console_scripts': ['mdk=src.main:main'],
    },
    install_requires=[
        'Click>=7',
        'colorama>=0.4',
        'docker-compose>=1.22',
        'pyyaml>=5.1',
        'requests>=2.22',
    ],
    license='MIT',
    long_description=long_description,
    long_description_content_type='text/markdown',
    name='mdk',
    packages=find_packages(),
    python_requires='>=3',
    url='https://matician.com/',
    version='1.1',
)
