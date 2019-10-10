#!/usr/bin/env python

from setuptools import find_packages, setup

__version__ = '2.0.5'

requires = [
    'arrow>=0.15.0,<0.16.0',
    'emails>=0.5.15,<0.6.0',
    'redis>=3.3.0,<3.4.0',
    'schematics>=2.1.0,<2.2.0',
    'SQLAlchemy-Utils>=0.34.0,<0.35.0',
    'SQLAlchemy>=1.3.0,<1.4.0',
    'toml>=0.10.0,<0.11.0',
]

DESCRIPTION = """This is Danqing's shared Python library, for [the better Danqing](https://www.danqing.co).

This library provides convenient APIs for dealing with SQLAlchemy, Redis, configurations, logging, and many other things. The full documentation can be found at the [documentation site](https://dqpy.danqing.io).
"""

setup(
    name='dqpy',
    version=__version__,
    description='Danqing\'s shared Python library',
    long_description=DESCRIPTION,
    long_description_content_type='text/markdown',
    author='Danqing Liu',
    author_email='code@danqing.io',
    url='https://github.com/danqing/dqpy',
    packages=find_packages(),
    install_requires=requires,
    extras_require={
        'mysql': ['PyMySQL>=0.9.3,<0.10.0'],
        'psql': ['psycopg2>=2.8.0,<2.9.0'],
    },
    entry_points={
        'console_scripts': ['dbadmin=dq.dbadmin:main'],
    },
    zip_safe=True,
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ),
)
