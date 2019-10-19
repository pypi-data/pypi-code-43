#! /usr/bin/env python
# coding: utf-8

import socket

__author__ = '鹛桑够'


def is_listen(port, host="127.0.0.1"):
    sock = socket.socket()
    address = (host, port)
    result = sock.connect_ex(address)
    if result == 0:
        return True
    else:
        return False
