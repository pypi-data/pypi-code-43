# -*- coding: utf-8 -*-

# Learn more: https://github.com/kennethreitz/setup.py

from setuptools import setup, find_packages

setup(
    name='swarm_lib',
    version='0.0.1',
    description='A Library for accessing the Swarm network written in Python',
    author='Geovane Fedrecheski',
    packages=find_packages(exclude=('tests', 'docs'))
)

print(find_packages())
