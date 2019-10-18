#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : tql-cloudml.
# @File         : bert
# @Time         : 2019-06-06 21:03
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : 

import os
import socket
# from restful_api import Api

ip = socket.gethostbyname(socket.getfqdn(socket.gethostname()))
print("#" * 100)
print(ip)
print("#" * 100)
BERT_PATH = "/fds/data/wv/chinese_L-12_H-768_A-12/"

print("#" * 100)
os.popen('bert-serving-start -model_dir %s -num_worker=4 -max_seq_len 128' % BERT_PATH).read()
# os.popen('nohup bert-serving-start -model_dir %s -num_worker=4 &' % BERT_PATH).read()
print("#" * 100)
