# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='swarm_lib',
    version='0.0.4',
    description='A Library for accessing the Swarm network written in Python',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Geovane Fedrecheski',
    packages=find_packages(exclude=('tests', 'docs'))
)

print(find_packages())
