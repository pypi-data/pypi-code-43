#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""The setup script."""
from setuptools import find_packages
from setuptools import setup

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements = [
    "isodate",
    "lxml",
    "requests",
    "signxml",
    "pytz",
    "python-dateutil",
    "pony",
    "pem",
]

setup_requirements = ["pytest-runner"]

test_requirements = ["pytest", "factory-boy", "pytest-ponyorm", "pytest-cov"]

setup(
    author="Carbon Coop",
    author_email="peter@carbon.coop",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.7",
    ],
    description="OpenADR Virtual End Node",
    install_requires=requirements,
    license="Apache Software License 2.0",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="pyoadr_ven",
    name="pyoadr_ven",
    packages=find_packages(include=["pyoadr_ven"]),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://carboncoop.gitlab.io/pyoadr-ven/",
    version="0.4.0",
    zip_safe=False,
)
