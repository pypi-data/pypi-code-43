#!/usr/bin/env python
# coding=utf-8
# 
# to build:
#   python setup.py sdist bdist_wheel
# 

from setuptools import setup, find_packages

setup(
    name='a3cosmos',
    version='0.9.1',
    description=(
        'A Python Package of A3COSMOS Astronomical Data and Catalog Utilities.'
    ),
    keywords="a3cosmos astronomical data and catalog utilities",
    long_description=open('README.rst').read(),
    author='A3COSMOS Team',
    author_email='dzliu@mpia.de',
    maintainer='A3COSMOS Team',
    maintainer_email='dzliu@mpia.de',
    license='BSD License',
    packages=find_packages(),
    platforms=["all"],
    url='https://sites.google.com/view/a3cosmos',
    project_urls={
        #"Bug Tracker": "https://bugs.example.com/HelloWorld/",
        "Documentation": "https://sites.google.com/view/a3cosmos/code/code-a3cosmos",
        #"Source Code": "https://code.example.com/HelloWorld/",
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        #'Development Status :: 5 - Production/Stable',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Scientific/Engineering :: Astronomy',
    ],
    install_requires=[
        'numpy',
        'astropy',
        'matplotlib',
        'requests-toolbelt',
    ], 
    include_package_data=True,
    #package_data={
    #    'project': ['default_data.json', 'other_datas/default/*.json']
    #},
    #data_files=
)

