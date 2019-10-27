# Copyright 2017 Brandon Schlueter

from setuptools import setup, find_packages


with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()

setup(
    name='yasjenkins',
    description='A Jenkins handler for YAS',
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    version='1.0-rc1',
    packages=find_packages(),
    install_requires=[
        'yas',
        'python-jenkins'
    ],
    classifiers=[
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python",
    ]
)
