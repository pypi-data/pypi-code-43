#!/usr/bin/env python
# coding=utf-8

from setuptools import setup, find_packages

setup(
    name='exobject',
    version=0.3,
    description=(
        'Extend Object Code'
    ),
    long_description=open('README.rst').read(),
    author='LenShang',
    author_email='lenshang@qq.com',
    maintainer='LenShang',
    maintainer_email='lenshang@qq.com',
    license='BSD License',
    packages=find_packages(),
    platforms=["all"],
    url='',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries'
    ],
    install_requires=[
        'python-dateutil'
    ]
)