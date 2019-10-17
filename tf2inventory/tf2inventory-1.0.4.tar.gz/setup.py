#!/usr/bin/env python

from distutils.core import setup

from setuptools import find_packages

setup(
    name='tf2inventory',
    version='1.0.4',
    description='Ansible inventory generator from a terraform',
    author='Omar Diaz',
    author_email='zcool2005@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
      'Click',
      'Jinja2',
    ],
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'tf2inventory=tf2inventory:tool',
        ]
    },
)
