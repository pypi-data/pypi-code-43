#!/usr/bin/python
# -*-coding: utf-8 -*-

from os import path

from setuptools import setup

here = path.abspath(path.dirname(__file__))

setup(
    name="iplot",
    description="IPlot is a plotting library",
    keywords="iplot",
    long_description="placeholder",
    license='GPL',
    author="Guangyang Li",
    author_email="mail@guangyangli.com",
    url="https://github.com/gyli/iplot",
    packages=['iplot'],
    classifiers=[
        'Programming Language :: Python :: 3.7',
    ],
)
