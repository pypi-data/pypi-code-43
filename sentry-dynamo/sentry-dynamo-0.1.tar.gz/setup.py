#!/usr/bin/env python
"""
sentry-dynamo
================
A Sentry NodeStorage implementation for AWS's DynamoDB database
:copyright: (c) 2015 Flipboard Inc.
"""
from setuptools import setup, find_packages

setup(
	name='sentry-dynamo',
	version='0.1',
	author='Dusan Jovanovic',
	author_email='dusan@flipboard.com',
	description='A Sentry Dynamo NodeStorage library',
	package_dir={'': 'src'},
	packages=find_packages('src', exclude=['sentry_dynamo.test']),
	install_requires=['sentry>=7.7.0', 'boto3>=1.1.4']
)
