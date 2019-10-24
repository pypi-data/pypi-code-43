#!/usr/bin/env python

import os
from os import path
import setuptools
import tingg

# os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
    name="qatingg",
    version=tingg.__version__,
    packages=setuptools.find_packages(),
    include_package_data=True,
    license='GPLv3+',
    description='Cellulant QA adapter',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://tingg.africa",
    author="S.Kingori",
    author_email="samson.mwangi@cllulant.com",
    install_requires=[
        'pycryptodome',
        'requests'
    ],
    tests_require=[
        'nose'
    ],
    test_suite='nose.collector',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content'
    ],
    python_requires='>=3.7',
)
