#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : tql-CLI.
# @File         : info
# @Time         : 2019-07-25 14:19
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : 
import socket

def ip():
    hostname = socket.getfqdn(socket.gethostname())
    localhost = socket.gethostbyname(hostname)
    print(hostname)
    print(localhost)
