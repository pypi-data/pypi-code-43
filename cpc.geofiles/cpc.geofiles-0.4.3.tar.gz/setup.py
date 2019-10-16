#!/usr/bin/env python
# -*- coding: utf-8 -*-


from setuptools import find_packages

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.md') as readme_file:
    readme = readme_file.read()

with open('CHANGELOG.md') as history_file:
    history = history_file.read()

requirements = ['cpc.geogrids', 'numpy', 'cpc.units', 'jinja2', 'xarray']

setup(
    name="cpc.geofiles",
    version='v0.4.3',
    description="CPC geospatial file interaction (reading, writing, etc.)",
    long_description=readme + '\n\n' + history,
    author="Mike Charles",
    author_email='mike.charles@noaa.gov',
    url="https://github.com/noaa-nws-cpc/cpc.geofiles",
    packages=find_packages(),
    namespace_packages=['cpc'],
    include_package_data=True,
    install_requires=requirements,
    license="CC",
    zip_safe=False,
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering :: Atmospheric Science',
        'License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication',
    ],
)
