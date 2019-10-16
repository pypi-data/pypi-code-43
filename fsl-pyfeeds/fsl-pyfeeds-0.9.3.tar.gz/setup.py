#!/usr/bin/env python
#
# setup.py - setuptools configuration for installing pyfeeds.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#


import os.path as op

from setuptools import setup
from setuptools import find_packages


basedir = op.dirname(__file__)

with open(op.join(basedir, 'requirements.txt'), 'rt') as f:
    install_requires = [i.strip() for i in f.readlines()]

with open(op.join(basedir, 'README.md'), 'rt') as f:
    readme = f.read()

version = {}
with open(op.join(basedir, "pyfeeds", "__init__.py")) as f:
    for line in f:
        if line.startswith('__version__'):
            exec(line, version)
            break
version = version['__version__']

setup(

    name='fsl-pyfeeds',
    version=version,
    description='FSL testing framework',
    long_description=readme,
    long_description_content_type='text/markdown',
    url='https://git.fmrib.ox.ac.uk/fsl/pyfeeds',
    author='Paul McCarthy',
    author_email='pauldmccarthy@gmail.com',
    license='Apache License Version 2.0',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: Free for non-commercial use',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries :: Python Modules'],

    packages=find_packages(exclude=('doc')),
    install_requires=install_requires,
    entry_points={
        'console_scripts' : [
            'pyfeeds = pyfeeds.main:main',
        ]
    }
)
