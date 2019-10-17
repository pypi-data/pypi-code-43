"""
Copyright (c) 2019, TransChain.

This source code is licensed under the Apache 2.0 license found in the
LICENSE file in the root directory of this source tree.
"""

from marshmallow import fields
from base64 import b64encode, b64decode


class BytesField(fields.Field):
    """ BytesField allows to serialize and deserialize a bytes object. """

    def _serialize(self, value: bytes, attr, obj, **kwargs) -> str:
        if value is None:
            return ""
        return b64encode(value).decode("utf-8")

    def _deserialize(self, value: str, attr, data, **kwargs) -> bytes:
        return b64decode(value.encode("utf-8"))
