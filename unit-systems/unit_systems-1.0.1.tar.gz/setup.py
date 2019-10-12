from setuptools import setup

setup(
name='unit_systems',
version='1.0.1',
author='Nicolas Deutschmann',
author_email='nicolas.deutschmann@gmail.com',
packages=['unit_systems'],
url='https://github.com/ndeutschmann/py-unit',
license='LICENSE.txt',
description='Physical unit_systems in python',
long_description=open('README.md').read(),
   classifiers=[
      "Programming Language :: Python :: 3",
      "License :: OSI Approved :: MIT License",
      "Operating System :: OS Independent",
   ],
install_requires=[
   "sympy"
],
)
