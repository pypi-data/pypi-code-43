"""
Copyright (c) 2019, TransChain.

This source code is licensed under the Apache 2.0 license found in the
LICENSE file in the root directory of this source tree.
"""

from datetime import datetime
from katena_chain_sdk_py.entity.tx_data_interface import TxData
from marshmallow import fields
from katena_chain_sdk_py.entity.tx_data import TxDataSchema
from katena_chain_sdk_py.serializer.base_schema import BaseSchema
from katena_chain_sdk_py.serializer.utc_datetime_field import UTCDatetimeField


class TxDataState:
    """ TxDataState wraps a TxData and additional values in order to define the unique state to be signed. """

    def __init__(self, chain_id: str, nonce_time: datetime, data: TxData):
        """ TxDataState constructor. """
        self.chain_id = chain_id
        self.nonce_time = nonce_time
        self.data = data


class TxDataStateSchema(BaseSchema):
    """ TxDataStateSchema allows to serialize and deserialize TxDataState. """
    __model__ = TxDataState
    chain_id = fields.Str()
    data = fields.Nested(TxDataSchema)
    nonce_time = UTCDatetimeField()
