#!/usr/bin/env python
# setup.py - pip script for cbcreator
#
# Copyright 2018-2019 Zhang Maiyun
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from setuptools import setup
try:
    import py2exe
except ImportError:
    pass

setup(
    name="cbcreator",
    version="1.0",
    description="Automatic class band creator",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Zhang Maiyun",
    author_email="myzhang1029@hotmail.com",
    url="https://github.com/myzhang1029/cbcreator",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ],
    python_requires='>=3.5',
    packages=["cbcreator"],
    install_requires=["pillow"],
    package_data={"cbcreator": ["resources/**/*.*"]},
    entry_points={
        "console_scripts": [
            "cbcreator = cbcreator.cbcreator:start"
        ]
    }
)
