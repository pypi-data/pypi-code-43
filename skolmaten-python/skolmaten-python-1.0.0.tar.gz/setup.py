# -*- coding: utf-8 -*-

import setuptools

with open("README.md") as fp:
    long_description = fp.read()

setuptools.setup(
    name="skolmaten-python",
    version="1.0.0",
    author="Simon Lövskog",
    author_email="simon@lovskog.eu",
    description="An python wrapper for the skolmaten service.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/simoncircle/skolmaten-python",
    packages=setuptools.find_packages(),
    license="MIT",
    install_requires=[
        "requests",
        "xmltodict",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)