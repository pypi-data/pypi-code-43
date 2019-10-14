# -*- coding: utf-8 -*-
from setuptools import setup


long_description = u"""
This is package is dedicated to image processing, flatifield correction, phase retrieval and X-ray tomography.
There is no clear description yet so please contact me (Maxim Polikarpov, polikarpov.maxim@mail.ru) in case you would like to use this package and get some guidance.

MIT License, Copyright (c) 2019 Maxim Polikarpov
"""


setup(
    name='maximus48',
    version='0.3.5',
    description='Useful tools for image processing & X-ray tomography',
    keywords=['tomography', 'reconstruction', 'imaging'],
    long_description=long_description,
    author='Maxim Polikarpov',
    author_email='polikarpov.maxim@mail.ru',
    url='https://github.com/maximka48/maximus48',
    platforms='OS Independent',
    license='MIT License',
    packages=['maximus48'])
