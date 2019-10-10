#!/usr/bin/env python3
# coding: utf8
# Copyright (C) 2019 Maciej Dems <maciej.dems@p.lodz.pl>
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of GNU General Public License as published by the
# Free Software Foundation; either version 3 of the license, or (at your
# opinion) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
from subprocess import Popen, PIPE

from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()


def version():
    """Find current version form git"""
    try:
        p = Popen(['git', 'describe', '--abbrev=0'],
                  stdout=PIPE, stderr=PIPE, encoding='utf8')
        p.stderr.close()
        version = p.stdout.read().strip()
    except:
        version = '0.0'
    print("version", version)
    return version


setup(
    name='PyRobbo',
    version=version(),
    packages=['robbo', 'robbo.sprites'],
    description='Clone of an old 8-bit Atari game Robbo',
    long_description=readme(),
    url='http://github.com/macdems/pyrobbo',
    author='Maciej Dems',
    author_email='macdems@gmail.com',
    license='GPL3',
    python_requires='>=3',
    install_requires=[
        'pygame',
        'PyYAML',
        'appdirs',
        'setuptools'
    ],
    package_data={
        'robbo': ['sounds/*.wav', 'levels/*.dat', 'skins/*/*.png']
    },
    entry_points={
        'console_scripts': ['pyrobbo=robbo:main']

    }
)
