"""
Copyright (c) 2019, TransChain.

This source code is licensed under the Apache 2.0 license found in the
LICENSE file in the root directory of this source tree.
"""

from marshmallow import fields
from datetime import datetime

RFC3339_MICRO_ZERO_PADDED = "%Y-%m-%dT%H:%M:%S.%fZ"


class UTCDatetimeField(fields.Field):
    """ UTCDatetimeField allows to serialize and deserialize a datetime object. """

    def _serialize(self, value: datetime, attr, obj, **kwargs) -> str:
        if value is None:
            return ""
        return value.strftime(RFC3339_MICRO_ZERO_PADDED)

    def _deserialize(self, value: str, attr, data, **kwargs) -> datetime:
        return datetime.strptime(value, RFC3339_MICRO_ZERO_PADDED)
