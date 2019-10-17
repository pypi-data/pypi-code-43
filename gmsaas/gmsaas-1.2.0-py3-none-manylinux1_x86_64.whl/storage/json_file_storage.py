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
File Storage using JSON format
"""

import os
import json

from .storage import BaseStorage


class JsonFileStorage(BaseStorage):
    """ Storage implementation that keeps object in a json file """

    def __init__(self, filename, permission_flags=None):
        self.filename = filename
        self.permission_flags = permission_flags

    def get(self, key):
        """ Get a value for key from storage """
        data = self._load_dict()
        if data:
            return data.get(key)
        return None

    def put(self, key, value):
        """ Save a value for key to storage """
        data = self._load_dict() or {}
        data[key] = value
        self._save_dict(data)

    def remove(self, key):
        """ Remove a key/value from storage """
        data = self._load_dict() or {}
        if key in data:
            del data[key]
            self._save_dict(data)

    def get_all(self):
        """ Get all key/value from storage """
        data = self._load_dict() or {}
        return data

    def _load_dict(self):
        try:
            with open(self.filename, "r") as json_file:
                return json.load(json_file)
        except:
            return {}

    def _save_dict(self, data):
        with open(self.filename, "w") as json_file:
            json.dump(data, json_file, indent=4)
            if self.permission_flags:
                os.chmod(self.filename, self.permission_flags)
