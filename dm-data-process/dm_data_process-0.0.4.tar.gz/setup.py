# coding: utf-8
"""
Created on 2018年5月28日

@author: Damon
"""
from setuptools import setup, find_packages
setup(name='dm_data_process',
      version='0.0.4',
      description='This is a sample package',
      author='Damon',
      author_email='5178646@qq.com',
      license='MIT',
      packages=find_packages(exclude=['data_process'])
      )
