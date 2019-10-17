#!/usr/bin/env python
"""chaostoolkit AWS builder and installer"""
import os
import sys
import io

import setuptools


name = 'vztcdpchaos-aws'
desc = 'vzt-cdp-chaos extension for AWS'

classifiers = [

    'Intended Audience :: Developers',
    'License :: Freely Distributable',
    'Operating System :: OS Independent',
    'License :: OSI Approved :: Apache Software License',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: Implementation',
    'Programming Language :: Python :: Implementation :: CPython'
]
author = 'vzt-cdp'
license = 'Apache License Version 2.0'
packages = [
    'cdpchaosaws',
    'cdpchaosaws.ecs',
    'cdpchaosaws.ec2',
    'cdpchaosaws.eks',
    'cdpchaosaws.iam',
    'cdpchaosaws.elbv2',
    'cdpchaosaws.asg',
    'cdpchaosaws.awslambda',
    'cdpchaosaws.cloudwatch',
    'cdpchaosaws.rds'
]


setup_params = dict(
    name=name,
    version='0.1.7',
    description=desc,
    classifiers=classifiers,
    author=author,
    license=license,
    packages=packages,
    include_package_data=True,
    install_requires=['aws-requests-auth',
    'boto3',
    'chaostoolkit-lib>=1.7.0',
    'requests',
    'cdpchaostoolkit'

    ]
)


def main():
    """Package installation entry point."""
    setuptools.setup(**setup_params)


if __name__ == '__main__':
    main()
