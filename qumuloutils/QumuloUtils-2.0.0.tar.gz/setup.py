# Copyright (c) 2016 Qumulo, Inc. All rights reserved.
#
# NOTICE: All information and intellectual property contained herein is the
# confidential property of Qumulo, Inc. Reproduction or dissemination of the
# information or intellectual property contained herein is strictly forbidden,
# unless separate prior written permission has been obtained from Qumulo, Inc.

# Copyright (c) 2016 Qumulo, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

from setuptools import setup

setup(
    name = "QumuloUtils",
    version = "2.0.0",
    packages = ['QumuloUtils'],
    author = "Michael Kade",
    author_email = "mkade@qumulo.com",
    keywords = "Qumulo QF2 API Helpers",
    license='LICENSE.txt',
    description = "Utility API routines to assist with the Qumulo clustered filesystem.",
    long_description=open('README.txt').read(),
    url = "http://www.qumulo.com/",
    install_requires=[
        "enum",
        "arrow",
        "logging",
        "python-dateutil",
        "qumulo-api",
        "multiprocessing",
    ],
)
