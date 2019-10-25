# coding=utf-8
from __future__ import absolute_import, print_function

import functools

from suanpan.proxy import Proxy
from suanpan import g


class Device(Proxy):
    MAPPING = {
        "zmq": "suanpan.device.zmq.ZMQDevice",
    }
