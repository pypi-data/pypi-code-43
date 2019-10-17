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
gmsaas crypto functions
"""

import base64


def cypher(value):
    """
    Cypher a value (string)
    """
    if not value:
        return ""

    return base64.b64encode(value.encode("utf-8")).decode("utf-8")


def decypher(cyphered_value):
    """
    Decypher a value (string)
    """
    if not cyphered_value:
        return ""

    return base64.b64decode(cyphered_value.encode("utf-8")).decode("utf-8")
