#!/usr/bin/env python3
#
# MIT License
#
# Copyright (c) 2019 Kelvin Gao
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import asyncio
import logging

from aqtlib import Object, util, config as conf
from ib_insync import IB

util.createLogger(__name__)

__all__ = ['Broker']


class Broker(Object):
    """Store class initilizer

    """

    RequestTimeout = 0

    defaults = dict(
        ib_port=conf.IB_PORT_4001_GW,
        ib_client=conf.IB_CLIENT_100_BROKER,
        ib_server=conf.IB_GW_SERVER_IP,
    )
    __slots__ = defaults.keys()

    def __init__(self, *args, **kwargs):
        Object.__init__(self, *args, **kwargs)

        # initilize class logger
        self._logger = logging.getLogger(__name__)

        self.ib = IB()

    def run(self):
        asyncio.get_event_loop().run_until_complete(self.ib.connectAsync(
                                                        self.ib_server,
                                                        self.ib_port,
                                                        self.ib_client
                                                    ))
        self._logger.info("Connection established...")
