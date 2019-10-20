#!/usr/bin/env python
from setuptools import find_packages, setup


project = "jedopo-py"
version = "0.0.6"


setup(
    name=project,
    version=version,
    author="Jeremiah Porten",
    author_email="jeremiah@gmail.com",
    description="A poc package",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/wheremiah",
    packages=find_packages(),
    python_requires='>=3.6',
    install_requires=[
        "click>=6.7",
    ],
    entry_points={
        "console_scripts": [
            "jedopo = jedopo.poc:main",
        ],
    },
)
