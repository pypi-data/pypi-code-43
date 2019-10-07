#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File name: setup
# Author: Oswaldo Cruz Simon
# Email: oswaldo_cs_94@hotmail.com
# Maintainer: Oswaldo Cruz Simon
# Date created: 03/10/19
# Date last modified: 03/10/19
# Project Name: scrapingtools

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    README = readme_file.read()

install_requires = [
    'redis>=3.3.8'
]

setup_args = dict(
    name='byprice-scrapingtools',
    version='0.0.8',
    description='Useful tools to scrape online stores',
    long_description_content_type="text/markdown",
    long_description=README,
    license='MIT',
    packages=['scrapingtools', 'scrapingtools.utils'],
    author='Oswaldo Cruz Simon',
    author_email='oswaldo@byprice.com',
    keywords=['scraping', 'ByPrice', 'Counter by hierarchy'],
    url='https://github.com/ByPrice/scraping-tools',
    install_requires=install_requires
)


if __name__ == '__main__':
    setup(**setup_args)
