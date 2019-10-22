#!/usr/bin/env python3


from setuptools import setup


VER = '0.2.1'


setup(
    name='parsewhen',
    version=VER,
    description='A library for extracting and parsing dates from English sentences.',
    license='MIT',
    packages=['parsewhen'],
    zip_safe=True,
    entry_points={
    'console_scripts': [
        'parsewhen = parsewhen.__main__:main'
        ]
    }
)
