#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup, find_packages, find_namespace_packages
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('VERSION') as fp:
    version = fp.read().strip()

install_requires = [
    'facebook_sdk==3.1.0',
    'facebook_business==4.0.5',
    'httplib2==0.13.1',
    'pandas==0.25.1',
    'SQLAlchemy==1.3.8',
    'google_api_python_client==1.7.11',
    'oauth2client==4.1.3',
]
setup(
    name='ge_sm',
    version=version,
    description="A python applications.",
    long_description=readme,
    author="Praekelt.org",
    author_email='dev@praekelt.org',
    packages=find_packages(),  # include all packages under src

    include_package_data=True,
    install_requires=install_requires,
    license="BSD",
    zip_safe=False,
    keywords='ge_sm',
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
    ]
)
