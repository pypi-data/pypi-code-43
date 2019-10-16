#!/usr/bin/env python
from setuptools import setup, find_packages
import os
__author__ = 'adamkoziol'

setup(
    name="ftir_renamer",
    version="0.9",
    packages=find_packages(),
    scripts=[os.path.join('ftir', 'renamer.py'),
             os.path.join('ftir', 'ftir_rename')],
    include_package_data=True,
    license='MIT',
    author='Adam Koziol',
    author_email='adam.koziol@canada.ca',
    description='File renamer for FTIR files',
    url='https://github.com/adamkoziol/ftir_renamer.git',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    install_requires=['pandas',
                      'OLCTools',
                      'xlrd'],
)
