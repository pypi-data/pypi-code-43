#!/usr/bin/env python
"""
cjr_db_connection - DB Connection class. Singleton class to reuse database connection.
"""
# This file is part of 'compute_job_recorder'
# A library for recording compute job progress.
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
# Purpose: DB Connection class. Singleton class to reuse database
#          connection, where possible.
#
# Author: Pete Bunting
# Email: pfb@aber.ac.uk
# Date: 08/02/2019
# Version: 1.0
#
# History:
# Version 1.0 - Created.

import logging
from distutils.version import LooseVersion

CJR_VERSION_MAJOR = 0
CJR_VERSION_MINOR = 1
CJR_VERSION_PATCH = 1

CJR_VERSION = str(CJR_VERSION_MAJOR) + "."  + str(CJR_VERSION_MINOR) + "." + str(CJR_VERSION_PATCH)
CJR_VERSION_OBJ = LooseVersion(CJR_VERSION)

CJR_COPYRIGHT_YEAR = "2019"
CJR_COPYRIGHT_NAMES = "Pete Bunting"
CJR_SUPPORT_EMAIL = "pete.bunting@aber.ac.uk"
CJR_WEBSITE = "https://www.remotesensing.info/cjr"

