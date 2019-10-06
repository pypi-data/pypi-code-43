# Copyright (C) 2019 Alteryx, Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
"""Helper functions for regular expressions."""

import re


def re_exact(val):
    """Create the regex exact match to the string passed in."""
    return "^" + re.escape(str(val)) + "$"


def re_exact_match(val):
    """Convert a list of strings to regex exact match."""
    if isinstance(val, str):
        return re_exact(str(val))

    try:
        val = list(val)
        return [re_exact(el) for el in val]
    except TypeError:
        raise TypeError("Input must be a string or a list of strings.")
