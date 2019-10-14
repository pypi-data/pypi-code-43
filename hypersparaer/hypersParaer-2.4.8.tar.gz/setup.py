#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import find_packages, setup

with open("README.rst", encoding='UTF-8') as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst", encoding='UTF-8') as history_file:
    history = history_file.read()

with open("paraer/__init__.py", "r" ) as init_fiel:
    version = init_fiel.readlines()[0].split("=")[1].strip().strip("'")

requirements = ["djangorestframework", "django", "django-rest-swagger"]

setup_requirements = []

test_requirements = ["pytest"]

setup(
    author="drinks",
    author_email="drinks.huang@hypers.com",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    description="Python Boilerplate contains all the boilerplate you need to create a Python package.",
    install_requires=requirements,
    license="MIT license",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="paraer",
    name="hypersParaer",
    packages=find_packages(include=["paraer"]),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/drinksober/paraer",
    version=eval(version),
    zip_safe=False,
)
