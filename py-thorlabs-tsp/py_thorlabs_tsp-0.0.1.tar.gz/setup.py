# -*- coding: utf-8 -*-
# Distutils setup script.
#
# run as
#   python3 setup.py sdist --formats=gztar,zip
#
from setuptools import setup
from _version import __version__

setup(
    name='py_thorlabs_tsp',
    packages=['py_thorlabs_tsp'],
    version=__version__,
    description='Controls for Thorlabs TSP01 sensor',
    author='Dzmitry Pustakhod, TU/e - PITC',
    author_email='d.pustakhod@tue.nl',
    url='http://phi.ele.tue.nl',
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
