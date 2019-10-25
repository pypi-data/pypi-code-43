#!/usr/bin/env python
# coding: utf-8

from setuptools import setup

from topa import VERSION

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='topa',
    version=VERSION,
    author='JIANG Wenjian',
    author_email='wenjian.jiang@foxmail.com',
    url='https://github.com/jwenjian/topa',
    description='A Top Output Python Analyzer',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='GPL-3.0',
    packages=['topa'],
    install_requires=['click'],
    entry_points={
        'console_scripts': [
            'topa=topa:main'
        ]
    }
)
