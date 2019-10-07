#
# Copyright (c) 2019 Mobikit, Inc.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
#

from setuptools import Command, find_packages, setup
from setup_base import base_kwargs

setup(
    **base_kwargs,
    packages=find_packages(),
    install_requires=[
        "numpy~=1.16.2",
        "pandas~=0.24.2",
        "pytest~=4.4.1",
        "geopandas~=0.5.0",
        "geopy~=1.19.0",
        "psycopg2-binary~=2.8.2",
    ],
)
