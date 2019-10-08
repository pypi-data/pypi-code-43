#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, Extension

setup(
    name='decor',
    version='2019.10.8',
    description='Detector corrections for azimuthal integration',
    author='Vadim Dyadkin',
    author_email='dyadkin@gmail.com',
    url='https://hg.3lp.cx/decor',
    license='GPLv3',
    install_requires=[
        'numpy',
        'cryio',
    ],
    packages=[
        'decor'
    ],
    ext_modules=[
        Extension(
            'decor._decor', [
                'src/decormodule.c',
                'src/distortion.c',
                'src/bispev.c',
                'src/bitmask.c',
            ],
            extra_compile_args=['-O3']),
    ],
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
)
