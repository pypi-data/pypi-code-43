#!/usr/bin/env python

from setuptools import setup, find_packages
import pkg_resources
import sys

# https://packaging.python.org/guides/single-sourcing-package-version/
with open('gostrat/version.py') as f :
    exec(f.read())

setup(name='gostrat',
      version=__version__
      ,description='Tool to stratify GO terms based on first significant parent'
      ,author='Adam Labadorf and the BU CAB Team'
      ,author_email='labadorf@bu.edu'
      ,install_requires=[
          'docopt',
          'future',
          'pandas',
          'setuptools',
          'goatools',
          'mygene',
          'networkx',
          'de_toolkit'
          ]
      ,packages=find_packages()
      ,entry_points={
        'console_scripts': [
          'gostrat=gostrat:main'
        ]
      }
      ,setup_requires=[
        'pytest-runner'
       ]
      ,tests_require=['pytest']
      ,url='https://bitbucket.org/bucab/gostrat'
      ,license='MIT'
      ,classifiers=[
        'Development Status :: 3 - Alpha'
        ,'Intended Audience :: Science/Research'
        ,'Environment :: Console'
        ,'License :: OSI Approved :: MIT License'
        ,'Programming Language :: Python :: 3'
        ,'Topic :: Scientific/Engineering :: Bio-Informatics'
      ]
      ,keywords=['bioinformatics','biology','sequencing','NGS']
      ,python_requires='~=3.3'
     )
