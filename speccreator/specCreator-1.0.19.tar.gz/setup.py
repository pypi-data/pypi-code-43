#!/usr/bin/env python
#-*- coding:utf-8 -*-

#############################################
# File Name: setup.py
# Author: handa
# Mail: 794363716@qq.com.com
# Created Time:  2018-09-19 18:18:18
#############################################


from setuptools import setup, find_packages

setup(
    name = "specCreator",
    version="1.0.19",
    keywords = ("pip", "spec", "specCreator", "podspec", "lib"),
    description = "create private pod, package framework Archive by Subspecs",
    long_description = "create private pod, package framework Archive by Subspecs",
    license = "MIT Licence",

    url="https://github.com/piaoying/specCreator",
    author="handa",
    author_email="794363716@qq.com",
    package_data={
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', '*.rst'],
        # include any *.msg files found in the 'test' package, too:
        'test': ['*.msg'],
    },
    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires=["pexpect", "PyYAML", "markdown==3.0.1"],
    entry_points={'console_scripts': [
        "specCreator = specCreator.specCreator:main",
    ]}
)