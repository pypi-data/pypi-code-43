"""
Copyright (c) 2019, TransChain.

This source code is licensed under the Apache 2.0 license found in the
LICENSE file in the root directory of this source tree.
"""

from marshmallow import fields
from katena_chain_sdk_py.serializer.base_schema import BaseSchema


class TxStatus:
    """ TxStatus is a tx blockchain status.
    0: OK
    1: PENDING
    >1: ERROR WITH CORRESPONDING CODE
    """
    def __init__(self, code: int, message: str):
        """ TxStatus constructor. """
        self.code = code
        self.message = message

    def get_code(self) -> int:
        return self.code

    def get_message(self) -> str:
        return self.message


class TxStatusSchema(BaseSchema):
    """ TxStatusSchema allows to serialize and deserialize a TxStatus. """
    __model__ = TxStatus
    code = fields.Int()
    message = fields.Str()
