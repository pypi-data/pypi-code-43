#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='grill-names',
    version='1.4.0',
    packages=find_packages(
        exclude=("*.tests", "*.tests.*", "tests.*", "tests", "*.docs", "*.docs.*", "docs.*", "docs")),
    package_data={
        'grill.tokens.ids': ['*.cfg'],
    },
    description='Name objects for digital content creation.',
    author='Christian López Barrón',
    author_email='chris.gfz@gmail.com',
    url='https://github.com/thegrill/grill-names',
    download_url='https://github.com/thegrill/grill-names/releases/tag/1.4.0',
    classifiers=['Programming Language :: Python :: 3.7'],
    extras_require={'docs': ['sphinx_autodoc_typehints', 'sphinx_rtd_theme']},
    install_requires=['naming'],
    namespace_packages=['grill']
)
