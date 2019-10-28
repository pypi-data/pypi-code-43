#!/usr/bin/env python
"""
setup.py: utilities to install this package
"""
from setuptools import find_packages, setup


setup(name='SgGo',
      version='0.5.1',
      description='view sg graph.',
      author='Wei Zou',
      author_email='wei.zou@corerain.com',
      packages=find_packages(),
      py_modules=['sg_go'],
      license="MIT",
      package_data={
        'sggo': [
          'static/js/*.js', 
          'static/css/*.css', 
          'templates/*.html']
      },
      install_requires=[
      	"Flask",
        "click>=6.7"
      ],
      entry_points='''
        [console_scripts]
        sg_go=sg_go:cli
      '''
      )
