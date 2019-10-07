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
    packages=find_packages(include=["mobikit_utils", "mobikit_utils.query_builder"]),
    install_requires=[]
)
