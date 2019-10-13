#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#

from setuptools import setup
from setuptools import find_packages

packages = find_packages()

setup(
    name = "labm8",
    version = "2019.10.13",
    description = "Utility libraries for doing science",
    long_description = open('README.md').read(),
    long_description_content_type="text/markdown",
    classifiers = ["Development Status :: 4 - Beta", "Environment :: Console", "Intended Audience :: Developers", "License :: OSI Approved :: Apache Software License", "Programming Language :: Python :: 3.6", "Programming Language :: Python :: 3.7", "Programming Language :: Python :: 3.8"],
    keywords = "utility library bazel protobuf",
    url = "https://github.com/ChrisCummins/labm8",
    author = "Chris Cummins",
    author_email = "chrisc.101@gmail.com",
    license = "Apache License, Version 2.0",
    packages=packages,
    install_requires=["SQLAlchemy==1.3.10", "Send2Trash==1.5.0", "absl-py==0.7.0", "checksumdir==1.0.5", "cycler==0.10.0", "decorator==4.3.0", "grpcio==1.18.0", "humanize==0.5.1", "kiwisolver==1.0.1", "matplotlib==2.2.0rc1", "mysqlclient==1.4.2.post1", "networkx==2.2", "numpy==1.16.4", "pandas==0.24.1", "protobuf==3.6.1", "py==1.5.2", "pyparsing==2.2.0", "python-dateutil==2.6.1", "pytz==2018.3", "scipy==1.2.1", "six==1.11.0"],
    zip_safe=False,
)
