# Copyright 2019 Genymobile
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
"""
Configuration file
"""

import os
import sys

import gmsaas


def _get_genymobile_path():
    if "GENYMOBILE_HOME" in os.environ:
        home_path = os.path.join(os.environ["GENYMOBILE_HOME"], ".Genymobile")
        try:
            os.makedirs(home_path, exist_ok=True)
        except OSError:
            print("GENYMOBILE_HOME is set to '{}', but this directory cannot be created.".format(home_path))
    elif sys.platform.startswith("win32"):
        home_path = "%LOCALAPPDATA%\\Genymobile"
    else:
        home_path = os.path.expanduser("$HOME/.Genymobile")
    return os.path.expanduser(os.path.expandvars(home_path))


CONFIG_DIR = os.path.join(_get_genymobile_path(), gmsaas.__application__)


def get_gmsaas_log_path():
    """
    Return path of gmsaas.log
    """
    return os.path.join(CONFIG_DIR, "gmsaas.log")


def get_gmadbtunneld_log_path():
    """
    Return path of gmadbtunneld.log
    """
    return os.path.join(CONFIG_DIR, "gmadbtunneld.log")
