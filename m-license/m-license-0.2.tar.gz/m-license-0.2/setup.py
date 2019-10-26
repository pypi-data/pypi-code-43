#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Author: ChungNT
    Company: MobioVN
    Date created: 04/10/2019
"""

from distutils.core import setup
from Cython.Build import cythonize

setup(name='m-license',
      version='0.2',
      description='Mobio libraries',
      url='https://github.com/mobiovn',
      author='MOBIO',
      author_email='contact@mobio.vn',
      license='MOBIO',
      packages=[],
      install_requires=['python-jose',
                        'Crypto'],
      ext_modules=cythonize(['./mobio/**/*.so'], compiler_directives=dict(always_allow_keywords=True)))
