#
# Copyright (c) 2019 Mobikit, Inc.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
#

from setuptools import setup, find_packages
from setup_base import base_kwargs

setup(
    **base_kwargs,
    packages=find_packages(
        include=[
            "mobikit",
            "mobikit.config",
            "mobikit.workspaces",
            "mobikit.workspaces.*",
        ]
    ),
    zip_safe=False,
    include_package_data=True,
    install_requires=["pandas>=0.24.2", "requests>=2.21.0", "mobikit-utils~=0.1.0"],
)
