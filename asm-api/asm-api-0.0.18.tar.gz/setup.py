#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Command line interface for Alphalogic Service Manager.
"""

import sys
import platform
from setuptools import setup
from asm_api.__init__ import __version__


cur = 'win32' if sys.platform == 'win32' else platform.linux_distribution()[0].lower()
ext = '.zip' if sys.platform == 'win32' else '.tar.gz'

bin_name = 'asm_api-%s-%s%s' % (cur, __version__, ext)


if __name__ == '__main__':

    with open('README.md', 'r') as fh:
        long_description = fh.read()

    setup(
        name='asm-api',
        version=__version__,
        description=__doc__.replace('\n', '').strip(),
        long_description=long_description,
        author='Alphaopen',
        author_email='mo@alphaopen.com',
        url='https://github.com/Alphaopen/asm_api',
        py_modules=['asm_api/asm_api', 'asm_api/__init__', 'asm_api/api/__init__', 'asm_api/api/client_api'],
        data_files = [('README', ['README.md'])],
        include_package_data=True,
        classifiers=(
            "Programming Language :: Python :: 2.7",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ),
        license='MIT',
        platforms=['linux2', 'win32'],
        install_requires=[
            'requests>=2.19.1',
        ],
    )