#!/usr/bin/env python3
from setuptools import setup, find_packages
from codecs import open # To use a consistent encoding
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

# get version number
defs = {}
with open(path.join(here, 'containator/defs.py')) as f:
    exec(f.read(), defs)

setup(
    name='containator',
    version=defs['__version__'],
    description=defs['app_description'],
    long_description=long_description,
    url='https://gitlab.com/beli-sk/containator',
    author="Michal Belica",
    author_email="code@beli.sk",
    license="GPL-3",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        ],
    keywords=['docker', 'container'],
    zip_safe=True,
    install_requires=[
        'docker-py',
        ],
    extras_require={
        'attach': 'dockerpty',
        },
    packages=['containator'],
    entry_points={
        'console_scripts': [
            'containator = containator:main',
            ],
        },
    )

