# -*- coding: utf-8 -*-

# @Date    : 2019-05-26
# @Author  : Peng Shiyu

from setuptools import setup, find_packages

"""
打包的用的setup必须引入，
"""

VERSION = '0.0.1'

setup(
    name='ggtool',
    version=VERSION,
    description="a command line tool which helpful",
    long_description='a command line tool which helpful',
    classifiers=[],  # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='ggtool',
    author='Peng Shiyu',
    author_email='pengshiyuyx@gmail.com',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    install_requires=[
        "fire>=0.2.1"
    ],
    entry_points={
        'console_scripts': [
            'ggtool = ggtool.main:main'
        ]
    }
)
