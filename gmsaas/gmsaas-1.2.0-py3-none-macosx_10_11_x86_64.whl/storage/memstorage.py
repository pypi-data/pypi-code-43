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
Memory storage
"""

from .storage import BaseStorage


class MemStorage(BaseStorage):
    """ Storage implementation that keeps object in memory """

    def __init__(self):
        self.store = {}

    def get(self, key):
        """ Get a value for key from storage """
        return self.store.get(key)

    def put(self, key, value):
        """ Save a value for key to storage """
        self.store[key] = value

    def remove(self, key):
        """ Remove a key/value from storage """
        if key in self.store:
            del self.store[key]

    def get_all(self):
        """ Get all key/value from storage """
        return dict(self.store)
