#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
***
Module:
***

 Copyright (C) Smart Arcs Ltd, registered in the United Kingdom.
 This file is owned exclusively by Smart Arcs Ltd.
 Unauthorized copying of this file, via any medium is strictly prohibited
 Proprietary and confidential
 Written by Dan Cvrcek <support@keychest.net>, 2019
"""
import base64
from multiprocessing import Queue
from unittest import TestCase
from foxyproxy.client_thread import ClientThread
from foxyproxy.csp import BaseCryptoService
from foxyproxy.upstream import BaseUpstream, BaseUpstreamConfig
__copyright__ = 'Smart Arcs Ltd'
__email__ = 'support@keychest.net'
__status__ = 'Development'


class TestBaseCryptoService(TestCase):
    def test_prioritize(self):

        queue_in = Queue()
        queue_out = Queue()
        queue_ack = Queue()
        queue_rest = Queue()
        queue_internal = Queue()
        upstream = BaseUpstream(BaseUpstreamConfig())
        signer = BaseCryptoService(upstream)
        _id = 0
        thread = ClientThread(signer, queue_in, queue_out, queue_ack, queue_rest, queue_internal, _id)
        in_data = "|0"
        _data = in_data.split('|')
        assert len(_data) == 2

        _data[0] = base64.b64decode(_data[0].encode()).decode()
        _data[1] = int(_data[1])

        new_list, priorities, last_priority = signer.prioritize("", _data[1])
        assert new_list == []
        assert priorities == {}
        assert  last_priority == 0
