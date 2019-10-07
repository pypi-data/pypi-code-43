#!/usr/bin/env python
import os
from setuptools import setup

with open("../README.md", "r") as fh:
    long_description = fh.read()

setup(
    name = "Swarmrob-Worker",
    version = "0.1",
    author = "Aljoscha Poertner",
    author_email = "aljoscha.poertner@fh-bielefeld.de",
    description = "An Orchestration Tool for Container-based Robot Applications",
    license = "GPL",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url = "https://github.com/aljoschap/swarmrob",
    packages=['swarmrob', 'swarmrob.swarmengine', 'swarmrob.dockerengine',
              'swarmrob.logger','swarmrob.utils'],
    entry_points = {
        'console_scripts' : ['swarmrob-worker = swarmrob.swarmrob:main']
    },
    data_files = [
    ('/swarmrob',['scripts/swarmrob.conf']),
    ],
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5"
    ],
    dependency_links=[
        'https://pypi.python.org/simple/'
    ]
)
