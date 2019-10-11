#!/usr/bin/env python

from distutils.core import setup

from setuptools import find_packages

setup(
    name='db_anonnymizer',
    version='1.0.1',
    description='Database anonnymized tool',
    author='Omar Diaz',
    author_email='omar.diaz@crosslend.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
      'Click',
      'dsnparse',
      'mysql-connector-python',
      'pyyaml',
      'Faker'
    ],
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'db_anonnymizer=db_anonnymizer:tool',
        ]
    },
)
