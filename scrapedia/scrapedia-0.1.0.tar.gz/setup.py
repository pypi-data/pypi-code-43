#!/usr/bin/env python
from os.path import join

from setuptools import setup, find_packages


MODULE_NAME = 'scrapedia'
REPO_NAME = 'scrapedia'

VERSION = open(join(MODULE_NAME, 'VERSION')).read().strip()


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()


setup(
    name=MODULE_NAME,
    description=('A scraper used for the extraction of brazilizan soccer'
                 ' historic data from the webpage futpedia.globo.com'),
    license=license,
    long_description=readme,
    long_description_content_type='text/markdown',
    url='https://github.com/LucasRGoes/{:s}'.format(REPO_NAME),
    download_url='https://github.com/LucasRGoes/{:s}/archive/{:s}.tar.gz'.format(REPO_NAME, VERSION),
    author='Lucas Góes',
    author_email='lucas.rd.goes@gmail.com',
    packages=find_packages(exclude=('tests', 'docs')),
    version=VERSION,
    install_requires=['beautifulsoup4==4.7.1', 'cachetools==3.1.1',
                      'pandas==0.24.2', 'requests==2.22.0',
                      'Unidecode==1.1.1'],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only'
    ],
    include_package_data=True
)
