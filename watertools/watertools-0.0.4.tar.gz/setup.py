# -*- coding: utf-8 -*-
"""
Created on Tue Aug 07 14:43:01 2018

@author: tih
"""
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="watertools",
    version="0.0.4",
    author="Tim Hessels",
    author_email="timhessels@hotmail.com",
    description="Tools for data collecting and data processing of remote sensed data.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TimHessels/watertools",
    packages=setuptools.find_packages(),
	install_requires=[
		'numpy==1.17.2',	
     	'beautifulsoup4==4.8.1',
		'GDAL==3.0.1',
		'h5py==2.10.0',
		'joblib==0.14.0',
		'netCDF4==1.5.1.2',
		'pandas==0.25.1',
		'paramiko==2.6.0',
		'pyproj==2.4.0',
     	'pyshp==2.1.0',
		'requests==2.22.0',
		'scipy==1.3.1',
		'pycurl'
    ],
    classifiers=(
	    "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ),
)