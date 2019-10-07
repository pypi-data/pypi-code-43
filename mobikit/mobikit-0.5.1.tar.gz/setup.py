#
# Copyright (c) 2019 Mobikit, Inc.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
#

from setuptools import setup
from types import SimpleNamespace
from setup_base import base_kwargs

setup(
    **base_kwargs,
    include_package_data=True,
    install_requires=[
        "mobikit-utils~=0.1.0",
        "bokeh>=1.0.0",
        "geopy>=1.19.0",
        "matplotlib>=3.0.3",
        "numpy>=1.16.1",
        "pandas>=0.24.2",
        "psycopg2-binary>=2.8.0",
        "requests>=2.21.0",
        "scikit-learn>=0.20.2",
        "scipy>=1.2.1",
        "geopy>=1.19.0",
        "plotly>=4.1.0",
        "scipy>=1.2.1",
        "shapely>=1.6.3",
        "geopandas>=0.5.0",
        "geopy>=1.19.0",
    ],
)
