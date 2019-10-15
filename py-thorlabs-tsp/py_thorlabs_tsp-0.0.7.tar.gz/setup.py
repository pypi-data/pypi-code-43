# -*- coding: utf-8 -*-
# Distutils setup script.
#
# run as
#   python3 setup.py sdist --formats=gztar,zip
#
from setuptools import setup
from _version import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='py_thorlabs_tsp',
    packages=['py_thorlabs_tsp'],
    version=__version__,
    description='Controls for Thorlabs TSP01 temperature and humidity sensor',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Dzmitry Pustakhod, TU/e - PITC',
    author_email='d.pustakhod@tue.nl',
    url='https://gitlab.com/dimapu/py_thorlabs_tsp',
    license='MIT License',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: Microsoft :: Windows :: Windows 7',
        'Operating System :: Microsoft :: Windows :: Windows 10',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Scientific/Engineering',
        'Topic :: System :: Hardware',
        'Topic :: System :: Hardware :: Hardware Drivers',
    ],
)
