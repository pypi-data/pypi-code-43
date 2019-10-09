#!/usr/bin/env python
import os

from setuptools import setup

SCRIPT_DIR = os.path.dirname(__file__)
if not SCRIPT_DIR:
    SCRIPT_DIR = os.getcwd()


def readme():
    with open("README.md") as f:
        return f.read()


setup(
    name="conversion",
    use_scm_version=True,
    author="Roberto Aguilar",
    author_email="r@rreboto.com",
    description="Utility functions to convert strings to Python types",
    long_description=readme(),
    long_description_content_type="text/markdown",
    packages=["conversion"],
    url="http://github.com/rca/conversion",
    license="LICENSE",
)
