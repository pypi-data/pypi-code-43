"""
Copyright (c) 2019, TransChain.

This source code is licensed under the Apache 2.0 license found in the
LICENSE file in the root directory of this source tree.
"""

from marshmallow import fields
from katena_chain_sdk_py.entity.api.tx_status import TxStatus, TxStatusSchema
from katena_chain_sdk_py.entity.tx import Tx, TxSchema
from katena_chain_sdk_py.serializer.base_schema import BaseSchema


class TxWrapper:
    """ TxWrapper wraps a tx and its status. """

    def __init__(self, tx: Tx, status: TxStatus):
        """ TxWrapper constructor. """
        self.tx = tx
        self.status = status

    def get_tx(self) -> Tx:
        return self.tx

    def get_status(self) -> TxStatus:
        return self.status


class TxWrapperSchema(BaseSchema):
    """ TxWrapperSchema allows to serialize and deserialize TxWrapper. """
    __model__ = TxWrapper
    tx = fields.Nested(TxSchema)
    status = fields.Nested(TxStatusSchema)
