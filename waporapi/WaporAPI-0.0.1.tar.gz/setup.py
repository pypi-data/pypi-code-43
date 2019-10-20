# -*- coding: utf-8 -*-
"""
Created on Tue Aug 07 14:43:01 2018

@author: tih
"""
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="WaporAPI",
    version="0.0.1",
    author="Tim Hessels",
    author_email="timhessels@hotmail.com",
    description="Tool for collecting WaPOR dataset automatically through python.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TimHessels/WaporAPI",
    packages=setuptools.find_packages(),
    classifiers=(
	    "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ),
)