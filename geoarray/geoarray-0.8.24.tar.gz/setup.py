#!/usr/bin/env python
# -*- coding: utf-8 -*-

# geoarray, A fast Python interface for image geodata - either on disk or in memory.
#
# Copyright (C) 2019  Daniel Scheffler (GFZ Potsdam, daniel.scheffler@gfz-potsdam.de)
#
# This software was developed within the context of the GeoMultiSens project funded
# by the German Federal Ministry of Education and Research
# (project grant code: 01 IS 14 010 A-C).
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup, find_packages
import warnings
from pkgutil import find_loader


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

version = {}
with open("geoarray/version.py") as version_file:
    exec(version_file.read(), version)

requirements = [
    'py_tools_ds>=0.10.0', 'numpy', 'matplotlib', 'six', 'gdal', 'shapely', 'geopandas', 'pandas', 'dill', 'mpld3',
    'geojson', 'folium', 'scikit-image', 'dask>=0.15.0'
    # dask is only indirectly needed but updating to >=0.15.0 resolves https://stackoverflow.com/questions/43833081/
    #   attributeerror-module-object-has-no-attribute-computation
    # 'holoviews', #  conda install --yes -c ioam bokeh holoviews ; \
    # git+https://github.com/matplotlib/basemap.git  # conda install --yes -c conda-forge basemap
    ]
setup_requirements = ['dask>=0.15.0']
test_requirements = requirements + ["coverage", "nose", "nose2", "nose-htmloutput", "rednose"]

setup(
    name='geoarray',
    version=version['__version__'],
    description="Fast Python interface for geodata - either on disk or in memory.",
    long_description=readme + '\n\n' + history,
    author="Daniel Scheffler",
    author_email='danschef@gfz-potsdam.de',
    url='https://gitext.gfz-potsdam.de/danschef/geoarray',
    packages=find_packages(),  # searches for packages with an __init__.py and returns them as properly formatted list
    package_dir={'geoarray': 'geoarray'},
    include_package_data=True,
    install_requires=requirements,
    license="GNU General Public License v3",
    zip_safe=False,
    keywords=['geoarray', 'geoprocessing', 'gdal', 'numpy'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements
)


# check for holoviews
if not find_loader('holoviews'):
    warnings.warn('You need to install holoviews manually (see www.holoviews.org) if you want to use interactive '
                  'plotting. It is not automatically installed.')

# check for basemap
if not find_loader('mpl_toolkits.basemap'):
    warnings.warn('You need to install basemap manually (see www./matplotlib.org/basemap) if you want to plot maps. '
                  'It is not automatically installed.')
