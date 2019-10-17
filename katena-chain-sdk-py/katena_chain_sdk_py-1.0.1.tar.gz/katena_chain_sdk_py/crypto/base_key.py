"""
Copyright (c) 2019, TransChain.

This source code is licensed under the Apache 2.0 license found in the
LICENSE file in the root directory of this source tree.
"""

import typing
from katena_chain_sdk_py.serializer.bytes_field import BytesField


class BaseKey:
    """ BaseKey holds a string key. """

    def __init__(self, key: bytes):
        """ BaseKey constructor. """
        self.key = key

    def get_key(self) -> bytes:
        return self.key


class KeyField(BytesField):
    """ KeyField allows to serialize and deserialize a BaseKey. """

    def __init__(self, model: typing.Type[BaseKey], **metadata):
        self.__model__ = model
        super().__init__(**metadata)

    def _serialize(self, value: BaseKey, attr, obj, **kwargs) -> str:
        return super()._serialize(value.get_key(), attr, obj, **kwargs)

    def _deserialize(self, value: str, attr, data, **kwargs) -> BaseKey:
        return self.__model__(super()._deserialize(value, attr, data, **kwargs))
