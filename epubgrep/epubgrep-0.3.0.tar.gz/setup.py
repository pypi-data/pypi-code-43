#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name="epubgrep",
    version="0.3.0",
    description='Grep through EPub files',
    author=u'Matěj Cepl',
    author_email='mcepl@cepl.eu',
    url='https://gitlab.com/mcepl/epubgrep',
    packages=find_packages(),
    test_suite='tests',
    install_requires=['epub_meta'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.7",
        "Environment :: Console",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
