"""
Copyright (c) 2019, TransChain.

This source code is licensed under the Apache 2.0 license found in the
LICENSE file in the root directory of this source tree.
"""

import abc


class TxData(abc.ABC):
    """ TxData interface defines the methods a concrete TxData must implement. """

    @abc.abstractmethod
    def get_type(self) -> str:
        pass

    @abc.abstractmethod
    def get_id(self) -> str:
        pass

    @abc.abstractmethod
    def get_namespace(self) -> str:
        pass

    @abc.abstractmethod
    def get_sub_namespace(self) -> str:
        pass
