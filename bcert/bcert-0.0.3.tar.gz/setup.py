#!/usr/bin/env python

# Python
import os

# Setuptools
from setuptools import setup, find_packages

# Bcert
from bcert import __version__

install_requirements = [
        "numpy",
        ]

try:
    import multiprocessing
except ImportError:
    install_requirements.append("multiprocessing")

try:
    import abc
except ImportError:
    install_requirements.append("abc")

setup(
    name="bcert",
    version=__version__,
    author="Xavier Valcarce",
    author_email="xvalcarce@protonmail.com",
    description="Bound certification of Lipschitz function on compact space",
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.md'),
        'rb').read().decode('utf-8'),
    license="BSD",
    keywords="certification bound Lipschitz",
    long_description_content_type="text/markdown",
    url="https://gitlab.com/plut0n/bcert",
    packages=find_packages(),
    install_requires=install_requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Operating System :: OS Independent",
    ],
)
