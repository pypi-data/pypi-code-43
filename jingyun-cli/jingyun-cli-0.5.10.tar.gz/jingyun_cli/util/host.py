#! /usr/bin/env python
# coding: utf-8

import socket

__author__ = '鹛桑够'


def get_default_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("114.114.114.114", 53))
    return s.getsockname()[0]


if __name__ == "__main__":
    ip = get_default_ip()
    print(ip)