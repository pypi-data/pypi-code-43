#!/usr/bin/env python
"""
Setup script for Compute Job Recorder. Use like this for Unix:

$ python setup.py install

"""
# This file is part of 'ComputeJobRecorder' 
# A tool for recording a compute job progress.
#
# Copyright 2019 Pete Bunting
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Purpose:  Installation of the ComputeJobRecorder software
#
# Author: Pete Bunting
# Email: pfb@aber.ac.uk
# Date: 30/07/2019
# Version: 1.0
#
# History:
# Version 1.0 - Created.

import setuptools
from distutils.core import setup
import os

setup(name='ComputeJobRecorder',
    version='0.1.1',
    description='A tool for recording a compute job progress.',
    author='Pete Bunting',
    author_email='pfb@aber.ac.uk',
    scripts=['bin/cjr_query.py', 'bin/cjr_record.py'],
    packages=['cjrlib'],
    package_dir={'cjrlib': 'cjrlib'},
    license='LICENSE.txt',
    url='https://www.remotesensing.info/compute_job_recorder',
    classifiers=['Intended Audience :: Developers',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python :: 3.5',
                 'Programming Language :: Python :: 3.6',
                 'Programming Language :: Python :: 3.7',
                 'Programming Language :: Python :: 3.8'])
