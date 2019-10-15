#!/usr/bin/env python3

from setuptools import setup

with open('README.md') as f:
    long_description = f.read()

setup(
    name = 'dxf2x',
    version = '0.0.1',
    author = 'redraiment',
    author_email = 'redraiment@gmail.com',
    url = 'http://github.com/redraiment/dxf2x',
    description = 'Convert between DXF, TSV, SVG, PXF(Protobuf) formats.',
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    packages = ['dxf2x'],
    install_requires = [],
    entry_points = {
        'console_scripts': [
            'dxf2x = dxf2x:dxf2x'
        ]
    },
    python_requires = '>=3.7'
)
