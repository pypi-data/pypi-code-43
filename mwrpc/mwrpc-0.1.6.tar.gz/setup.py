#!/usr/bin/env python
# coding=utf-8

from setuptools import setup, find_packages

setup(
    name='mwrpc',
    version='0.1.6',
    description='Yet Another RPC Framework.',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    author='MWR Organization',
    author_email='mwr@mwr.pub',
    url='https://github.com/MwrPub/mwrpc-py',
    py_modules=['mwrpc'],
    scripts=['mwrpc.py'],
    license='MIT',
    platforms='any',
    classifiers=['Operating System :: OS Independent',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: MIT License',
                 'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
                 'Topic :: Software Development :: Libraries :: Application Frameworks',
                 'Programming Language :: Python :: 3',
                 'Programming Language :: Python :: 3.4',
                 'Programming Language :: Python :: 3.5',
                 'Programming Language :: Python :: 3.6',
                 'Programming Language :: Python :: 3.7',
                 ],
)
