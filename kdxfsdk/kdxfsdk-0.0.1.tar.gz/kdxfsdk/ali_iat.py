# -*- coding: utf-8 -*-
import requests
import time
import hashlib
import base64
import json


class Iat(object):
    URL = "http://api.xfyun.cn/v1/service/v1/iat"
    APPID = "5cc5623f"
    API_KEY = "c41119709160ed5ea00d025e7bfadc2c"
    AUE = "raw"
    engine_type = "sms16k"

    def __init__(self, file_name):
        self.file_name = file_name

    def _get_body(self):
        bin_file = open(self.file_name, 'rb')
        data = {'audio': base64.b64encode(bin_file.read())}
        bin_file.close()
        return data

    def _get_header(self):
        cur_time = str(int(time.time()))
        param = dict()
        param["aue"] = self.AUE
        param["engine_type"] = self.engine_type
        param_content = json.dumps(param)
        param_base64 = str(base64.b64encode(param_content.encode('utf-8')))
        print("x_param:{}".format(param_base64))

        m2 = hashlib.md5()
        m2.update((self.API_KEY + cur_time + param_base64).encode('utf-8'))
        check_sum = m2.hexdigest()
        print('checkSum:{}'.format(check_sum))
        header = {
            'X-CurTime': cur_time,
            'X-Param': param_base64,
            'X-Appid': self.APPID,
            'X-CheckSum': check_sum,
            'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
        }
        print(header)
        return header

    def parse_speech(self):
        r = requests.post(self.URL, headers=self._get_header(), data=self._get_body())
        return r.content.decode('utf-8')
