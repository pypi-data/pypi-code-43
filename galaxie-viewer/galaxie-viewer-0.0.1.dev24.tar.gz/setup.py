#!/usr/bin/env python

# This will try to import setuptools. If not here, it fails with a message
try:
    from setuptools import setup, find_packages
except ImportError:
    raise ImportError("This module could not be installed, probably because"
                      " setuptools is not installed on this computer."
                      "\nInstall ez_setup ([sudo] pip install ez_setup) and try again.")

setup(
    packages=find_packages(exclude=["dist", "tests"]),
    python_requires='>=3.7',
    tests_require=['green'],
    setup_requires=['pbr'],
    pbr=True,
)
