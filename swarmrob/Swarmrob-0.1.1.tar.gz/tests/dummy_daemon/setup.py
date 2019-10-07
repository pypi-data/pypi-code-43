#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2018,2019 Aljoscha Pörtner
# Copyright 2019 André Kirsch
# This file is part of SwarmRob.
#
# SwarmRob is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SwarmRob is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SwarmRob.  If not, see <https://www.gnu.org/licenses/>.

import os

from setuptools import setup

setup(
    name="DaemonDummy",
    version="0.0.1",
    author="André Kirsch",
    author_email="andre.kirsch@fh-bielefeld.de",
    description="Test dummy daemon for testing SwarmRob",
    license="GPL v3",
    url="https://github.com/aljoschap/swarmrob",
    packages=['daemon_dummy', 'daemon_dummy.logger', 'daemon_dummy.utils'],
    entry_points={
        'console_scripts': ['swarmrob_dummy = daemon_dummy.daemon_dummy:main']
    },
    data_files=[
        ('/daemon_dummy/', ['requirements.txt'])
    ],
    classifiers=[
        "License :: OSI Approved :: GPL v3 License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5"
    ],
    dependency_links=[
        'https://pypi.python.org/simple/'
    ]
)
