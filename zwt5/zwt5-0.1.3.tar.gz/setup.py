# !/usr/bin/env python

from setuptools import setup
setup(name='zwt5',
version='0.1.3',
description='A silly package',
author='Wentao Zheng',
author_email='nkzhengwt@outlook.com',
url='',
packages=['zwt5', 'zwt5.adv'],
install_requires=['statsmodels','numpy','funsor'],
license = 'MIT',
python_requires='>=3',
)
