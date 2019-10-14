# -*- coding: utf-8 -*-
import setuptools
from setuptools import setup

setup(
    name="aws-eventbridge-rule-syncer",
    description="Provides rule syncer and rule evaluator for AWS Event Bridge",

    version="2.0.0",

    author="Akash Agarwal",
    author_email="agarwalakash45@gmail.com ",

    url="https://github.com/ackotech/aws-eventbridge-rule-syncer",
    license="BSD",

    install_requires=["boto3"],

    packages=setuptools.find_packages(),
    zip_safe=True,


    keywords=['aws', 'event-bridge', 'rules'],


    classifiers=[

        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Other Audience',

        'Natural Language :: English',

        'Operating System :: OS Independent',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS :: MacOS X',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',

        'Topic :: Software Development',

    ],
)
