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
"""Constant values used throughout the ayx_learn library."""

from enum import Enum, unique


NA_PLACEHOLDER = "ayx_na_placeholder"


@unique
class ColumnTypes(Enum):
    """Enum for supported column types."""

    CATEGORICAL = "CATEGORICAL"
    NUMERIC = "NUMERIC"
    BOOLEAN = "BOOLEAN"
    ID = "ID"
