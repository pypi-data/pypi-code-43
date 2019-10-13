#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
from setuptools import find_packages, setup

NAME = 'funity'
VERSION = '0.0.1'
DESCRIPTION = 'A Unity3d installation finder and a command line helper.'
HOME = Path(__file__).parent
README = (HOME / 'README.md').read_text()
CHANGELOG = (HOME / 'CHANGELOG.md').read_text()
AUTHOR = 'Elmer Nocon, fopoon'
AUTHOR_EMAIL = 'elmernocon@gmail.com'
LICENSE = 'MIT'
PLATFORMS = 'Any'
URL = 'https://github.com/fopoon/funity'
DOWNLOAD_URL = 'https://pypi.org/project/funity/'
CLASSIFIERS = [
    'Development Status :: 1 - Planning',
    'License :: OSI Approved :: MIT License',
    'Operating System :: MacOS :: MacOS X',
    'Operating System :: Microsoft :: Windows :: Windows 10',
    'Operating System :: Unix',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3 :: Only',
]

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description='\n\n'.join([README, CHANGELOG]),
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license=LICENSE,
    platforms=PLATFORMS,
    url=URL,
    download_url=DOWNLOAD_URL,
    classifiers=CLASSIFIERS,

    packages=find_packages(
        exclude=[
            "tests",
            "tests.*",
            "*.tests.*",
            "*.tests"
        ]
    ),
    zip_safe=False,
    package_data={
        'funity': [
            'data/*.cs',
            'data/Editor/*.cs'
        ],
    },
    install_requires=[
        'PyYAML',
    ],
    entry_points={
        'console_scripts': [
            'funity=funity.__main__:main'
        ]
    },
)
