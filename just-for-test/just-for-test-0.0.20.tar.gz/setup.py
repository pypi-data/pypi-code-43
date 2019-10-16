#!/usr/bin/env python
from setuptools import find_packages, setup

with open('README.rst', encoding='utf-8') as f:
    readme = f.read()

setup(
    name='just-for-test',
    version='0.0.20',
    url='https://github.com/codeif/just-for-test',
    project_urls={
        "Documentation": "https://just-for-test.readthedocs.io",
    },
    description='only for test.',
    long_description=readme,
    author='codeif',
    author_email='me@codeif.com',
    license='MIT',
    install_requires=['requests'],
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    packages=find_packages(),
    extras_require={
        "docs": [
            "sphinx",
        ],
    },
)
