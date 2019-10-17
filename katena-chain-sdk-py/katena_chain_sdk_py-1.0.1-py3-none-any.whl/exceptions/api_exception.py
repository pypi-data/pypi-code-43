"""
Copyright (c) 2019, TransChain.

This source code is licensed under the Apache 2.0 license found in the
LICENSE file in the root directory of this source tree.
"""

from marshmallow import fields
from katena_chain_sdk_py.serializer.base_schema import BaseSchema


class ApiException(Exception):
    """ ApiException allows to wrap API errors. """

    def __init__(self, code: int, message: str):
        """ ApiException constructor. """
        message_formatted = 'api error:\nCode : %s\nMessage : %s' % (code, message)
        super().__init__(message_formatted)
        self.code = code


class ApiExceptionSchema(BaseSchema):
    """ ApiExceptionSchema allows to serialize and deserialize ApiException. """
    __model__ = ApiException
    code = fields.Int()
    message = fields.Str()

    class Meta:
        additional_fields = fields.Raw()
