#!/usr/bin/env python
from __future__ import unicode_literals

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

long_description = (
    'Autosub is a utility for automatic speech recognition and subtitle generation. '
    'It takes a video or an audio file as input, performs voice activity detection '
    'to find speech regions, makes parallel requests to Google Web Speech API to '
    'generate transcriptions for those regions, (optionally) translates them to a '
    'different language, and finally saves the resulting subtitles to disk. '
    'It supports a variety of input and output languages (to see which, run the '
    'utility with --list-src-languages and --list-dst-languages as arguments '
    'respectively) and can currently produce subtitles in either the SRT format or '
    'simple JSON.'
)

setup(
    name='solomon',
    version='0.0.1',
    description='Solomon tools',
    long_description=long_description,
    author='ztimc',
    author_email='ztimcz@gmail.com',
    url='https://github.com/ztimc/solomon',
    include_package_data=True,
    packages=['solomon'],
    entry_points={
        'console_scripts': [
            'solomon = solomon:main',
        ],
    },
    install_requires=[
        'pbxproj>=2.6.0',
    ],
    license=open("LICENSE").read()
)
