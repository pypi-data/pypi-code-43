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
    version="0.0.2",
    author="Tim Hessels",
    author_email="timhessels@hotmail.com",
    description="Tools for data collecting and data processing of remote sensed data.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TimHessels/watertools",
    packages=setuptools.find_packages(),
	install_requires=[
		'numpy==1.17.2',	
        'Pillow>=5.2.0',
		'httplib2>=0.11.3',
		'lxml>=4.2.4',
        'oauth2client>=4.1.2',
		'asn1crypto==1.2.0',
		'bcrypt==3.1.7',
		'beautifulsoup4==4.8.1',
		'certifi==2019.9.11',
		'cffi==1.13.0',
		'cftime==1.0.3.4',
		'chardet==3.0.4',
		'cryptography==2.7',
		'GDAL==3.0.1',
		'h5py==2.10.0',
		'idna==2.8',
		'joblib==0.14.0',
		'mkl-service==2.3.0',
		'netCDF4==1.5.1.2',
		'pandas==0.25.1',
		'paramiko==2.6.0',
		'pycparser==2.19',
		'pycurl==7.43.0.3',
		'PyNaCl==1.3.0',
		'pyOpenSSL==19.0.0',
		'pyproj==2.4.0',
		'pyreadline==2.1',
		'pyshp==2.1.0',
		'PySocks==1.7.1',
		'python-dateutil==2.8.0',
		'pytz==2019.3',
		'requests==2.22.0',
		'scipy==1.3.1',
		'six==1.12.0',
		'soupsieve==1.9.4',
		'urllib3==1.25.6',
		'win-inet-pton==1.1.0',
		'wincertstore==0.2'
    ],
    classifiers=(
	    "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ),
)