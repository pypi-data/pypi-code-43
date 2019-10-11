#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from setuptools import setup


def get_long_description():
    with open("README.md", encoding="utf8") as f:
        return f.read()


def get_packages(package):
    return [
        dirpath
        for dirpath, dirnames, filenames in os.walk(package)
        if os.path.exists(os.path.join(dirpath, "__init__.py"))
    ]


setup(
    name='gql_ext',
    version='0.0.13',
    author='Max Ponomarev',
    author_email='ponomarev1802@mail.ru',
    url='https://github.com/lazy-labs/bff-graphql',
    python_requires=">=3.7",
    install_requires=[
        "aiodataloader==0.1.2",
        "aiohttp==3.5.4",
        "pyyaml==5.1.2",
        "tartiflette==0.12.4",
        "ujson==1.35",
        "asyncpg==0.18.3"
    ],
    license="BSD",
    description="The web framework",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    packages=get_packages("gql_ext"),
    include_package_data=True,
    data_files=[("", ["LICENSE"])],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP",
        "Programming Language :: Python :: 3.7",
    ],
    zip_safe=False,
)
