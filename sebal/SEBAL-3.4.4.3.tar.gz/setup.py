# -*- coding: utf-8 -*-
"""
Created on Tue Aug 07 14:43:01 2018

@author: tih
"""
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="SEBAL",
    version="3.4.4.3",
    author="Tim Hessels",
    author_email="timhessels@hotmail.com",
    description="Python module for Surface Energy Balance Algorithm for Land",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TimHessels/SEBAL",
    packages=setuptools.find_packages(),
	package_dir={'SEBAL': 'SEBAL'},
	package_data={'SEBAL': ['*.xlsx']},
	install_requires=[
        'Pillow',
		'h5py',
		'lxml',
		'netCDF4',
		'openpyxl',
		'numpy',
		'pandas',
		'scipy',
		'pyproj',
		'joblib'
    ],
    classifiers=(
	    "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ),
)