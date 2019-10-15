#!python
# -*- coding:utf-8 -*-
from __future__ import print_function
from setuptools import setup, find_packages

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name="BDPabc",
    version="0.0.1",
    author="Memory&Xinxin",
    author_email="memory_d@foxmail.com",
    description="free python games written by pygame",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/MemoryD/mxgames",
    packages=find_packages(),
    install_requires=[
        "pygame <= 1.9.5"
        ]
)
