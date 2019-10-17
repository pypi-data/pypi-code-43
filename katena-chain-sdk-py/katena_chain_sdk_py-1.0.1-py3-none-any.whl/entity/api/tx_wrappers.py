"""
Copyright (c) 2019, TransChain.

This source code is licensed under the Apache 2.0 license found in the
LICENSE file in the root directory of this source tree.
"""

from marshmallow import fields
from typing import List
from katena_chain_sdk_py.entity.api.tx_wrapper import TxWrapper, TxWrapperSchema
from katena_chain_sdk_py.serializer.base_schema import BaseSchema


class TxWrappers:
    """ TxWrappers wraps a list of TxWrapper with the total txs available. """

    def __init__(self, txs: List[TxWrapper], total: int):
        """ TxWrappers constructor. """
        self.txs = txs
        self.total = total

    def get_txs(self) -> List[TxWrapper]:
        return self.txs

    def get_total(self) -> int:
        return self.total


class TxWrappersSchema(BaseSchema):
    """ TxWrappersSchema allows to serialize and deserialize TxWrapper. """
    __model__ = TxWrappers
    txs = fields.List(fields.Nested(TxWrapperSchema))
    total = fields.Int()
