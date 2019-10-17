"""
Copyright (c) 2019, TransChain.

This source code is licensed under the Apache 2.0 license found in the
LICENSE file in the root directory of this source tree.
"""

from marshmallow import Schema, post_load
import typing


class BaseSchema(Schema):
    """ BaseSchema wraps a marshmallow Schema to configure marshalling and unmarshalling operation. """
    __model__ = None

    class Meta:
        ordered = True

    def dumps(self, obj: typing.Any, *args, many: bool = None, **kwargs) -> str:
        """ Redefines the dumps method to avoid space in separators. """
        return super().dumps(obj, *args, many=many, separators=(',', ':'), **kwargs)

    @post_load
    def make_model(self, data, **kwargs) -> typing.Any:
        """ Post load hook to instantiate a corresponding Model if defined. """
        if self.__model__ is not None:
            return self.__model__(**data)
        return data
