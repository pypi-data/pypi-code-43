import os
from setuptools import setup, find_packages

with open('README.md') as fh:
    LONG_DESCRIPTION = fh.read()


setup(
    name='GN',
    version='0.1',
    author="zhaofeng-shu33",
    install_requires=['networkx'],
    author_email="616545598@qq.com",
    packages = find_packages(),
    description="a hierachical community detection algorithm by Girvan Newman",
    url="https://github.com/zhaofeng-shu33/Girvan-Newman",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    license="Apache License Version 2.0",
)