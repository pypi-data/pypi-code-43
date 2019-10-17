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
""" Access to data storage """

import os
import stat

from ..settings import CONFIG_DIR

from .memstorage import MemStorage
from .json_file_storage import JsonFileStorage


__all__ = ["JsonFileStorage", "MemStorage", "get_config_storage"]


CONFIG_FILENAME = os.path.join(CONFIG_DIR, "config.json")
CONFIG_STORAGE = JsonFileStorage(CONFIG_FILENAME)

AUTH_FILENAME = os.path.join(CONFIG_DIR, "auth.json")
AUTH_STORAGE = JsonFileStorage(AUTH_FILENAME, stat.S_IRUSR | stat.S_IWUSR)


def get_config_storage():
    """ Get configuration storage implementation """
    os.makedirs(CONFIG_DIR, exist_ok=True)
    return CONFIG_STORAGE


def get_auth_storage():
    """ Get auth storage implementation """
    os.makedirs(CONFIG_DIR, exist_ok=True)
    return AUTH_STORAGE
