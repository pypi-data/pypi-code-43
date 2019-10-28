#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import find_packages, setup

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.md") as history_file:
    history = history_file.read()

with open("requirements/base.txt") as f:
    requirements = f.read().splitlines()
    dependency_links = []
    for req in requirements:
        if req.startswith("git+"):
            requirements.remove(req)
            dependency_links.append(req)

with open("requirements/test.txt") as f:
    test_requirements = f.read().splitlines()

setup(
    author="Jesse Burger",
    author_email="jesse@mintlab.nl",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: European Union Public Licence 1.2 (EUPL 1.2)",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    description="AMQP Client for minty project",
    setup_requires=["pytest-runner"],
    install_requires=requirements,
    dependency_links=dependency_links,
    license="EUPL license",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="minty_amqp",
    name="minty_amqp",
    packages=find_packages(include=["minty_amqp", "minty_amqp.*"]),
    package_data={"": ["*.json"]},
    test_suite="tests",
    tests_require=test_requirements,
    url="https://gitlab.com/minty-python/minty_amqp",
    version="2.0.1",
    zip_safe=False,
)
