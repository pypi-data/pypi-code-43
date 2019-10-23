# -*- coding: utf-8 -*-
"""
Created on Tue Aug 07 14:43:01 2018

@author: tih
"""
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="WaporTranslator",
    version="0.0.0",
    author="Tim Hessels",
    author_email="timhessels@hotmail.com",
    description="Python module for calculating Climate, Drought, Food Security, Irrigation, and Water Productivity indicators mostly based on the FAO's WaPOR datasets.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TimHessels/WaporTranslator",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ),
)