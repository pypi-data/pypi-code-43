from setuptools import find_packages, setup

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="dlx-lib",
    version="0.0.0",
    descriptions="Synthetic data generator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.6, <3.8",
    author="Kiyohito Kunii",
    url="https://github.com/921kiyo/dlx-lib",
)
