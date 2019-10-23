#!/usr/bin/env python3
from setuptools import find_packages
from setuptools import setup


setup(
    name='aorta',
    version='1.0.26',
    description='AMQP Durable Messaging Library',
    author='Cochise Ruhulessin',
    author_email='c.ruhulessin@ibrb.org',
    url='https://www.ibrb.org',
    install_requires=[
        'pytz',
        'python-qpid-proton==0.28.0',
	    'PyYAML>=5.1.2',
        'marshmallow>=3.0.1',
        'python-ioc>=1.3.11',
    ],
    packages=find_packages()
)
