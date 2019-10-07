#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('./src/genomoncology/README.md') as readme_file:
    readme = readme_file.read()

history = ""

tests_require = [
    "pytest-flake8 >= 1.0.2",
    "black >= 18.5b1",
    "ipython >= 6.4.0",
    "pytest >= 3.6.0",
    "pytest-cov >= 2.5.1",
    "pytest-mccabe >= 0.1",
    "white >= 0.1.2",
    "pytest-socket >= 0.2.0",
    "pytest-asyncio >= 0.8.0",
    "aioconsole >= 0.1.8",
    "addict >= 2.1.3",
    "requests >= 2.4",
]

setup(
    name="gocli",
    version='0.9.3',
    author="Ian Maurer",
    author_email='ian@genomoncology.com',

    packages=[
        "genomoncology",
        "genomoncology.kms",
        "genomoncology.cli",
        "genomoncology.parse",
        "genomoncology.pipeline",
        "genomoncology.pipeline.sinks",
        "genomoncology.pipeline.sources",
        "genomoncology.pipeline.sources.one_off_sources",
        "genomoncology.pipeline.transformers",
        "genomoncology.pipeline.transformers.tx",
        "gosdk",
        "govcf",
        "govcf.calculate_vaf",

    ],
    package_dir={
        '': 'src'
    },

    package_data={
        '': ["*.yaml", "*.bed", "*.txt", "*.tsv", "*.csv"]
    },

    include_package_data=True,

    tests_require=tests_require,

    install_requires=[
        "specd >= 0.8.1",
        "backoff >= 1.5.0",
        "click == 6.7",
        "structlog >= 18.1.0",
        "colorama >= 0.3.9",
        "pysam >= 0.14.1",
        "ujson >= 1.3.5",
        "intervaltree == 2.1.0",
        "glom >= 18.1.1",
        "cytoolz >= 0.9.0.1",
        "pygments >= 2.2.0",
        "jsonschema[format] >= 2.6.0",
        "flask == 1.0.2",
    ],

    setup_requires=[
        'pytest-runner',
    ],

    license="Proprietary",
    keywords='Bioinformatics HGVS VCF Clinical Trials Genomics',

    description="gocli",
    long_description="%s\n\n%s" % (readme, history),

    entry_points={
        'console_scripts': [
            'gocli=genomoncology.main:main',
        ],
    },

    classifiers=[
        'License :: Other/Proprietary License',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
    ],
)
