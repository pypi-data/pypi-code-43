from setuptools import setup


setup(
name='unit_systems',
version='1.0.2',
author='Nicolas Deutschmann',
author_email='nicolas.deutschmann@gmail.com',
packages=['unit_systems'],
url='https://github.com/ndeutschmann/py-units',
license='LICENSE.txt',
description='Physical unit_systems in python',
long_description=open('README.md').read(),
long_description_content_type='text/markdown',
   classifiers=[
      "Programming Language :: Python :: 3",
      "License :: OSI Approved :: MIT License",
      "Operating System :: OS Independent",
   ],
install_requires=[
   "sympy"
],
)
