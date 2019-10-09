#!/usr/bin/env python3
from setuptools import find_packages, setup
import os

try:
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, 'README.md'), encoding='utf-8') as readme:
        long_description = readme.read()
except:
    pass

setup(
    name='jdTranslationHelper',
    version='1.3',
    description='A simple API for translating your programs.',
    long_description="Look at the Homepage for the documentation",
    url='https://gitlab.com/JakobDev/jdTranslationHelper',
    author='JakobDev',
    classifiers=[
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
    ],
    keywords='translation localization JakobDev ',
    packages=find_packages(),
)
