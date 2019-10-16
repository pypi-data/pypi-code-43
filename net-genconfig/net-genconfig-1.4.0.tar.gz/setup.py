#!/usr/bin/env python3


import setuptools

import net_genconfig


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="net-genconfig",
    version=net_genconfig.__version__,
    author="Robert Franklin",
    author_email="rcf34@cam.ac.uk",
    description="Network device configuration generator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.uis.cam.ac.uk/",
    packages=setuptools.find_packages(),
    install_requires=[
        "jinja2",
        "netaddr",
        "pyyaml",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
