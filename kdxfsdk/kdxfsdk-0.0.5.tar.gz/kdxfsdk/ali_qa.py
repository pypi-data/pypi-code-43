#-*- coding: utf-8 -*-
import requests
import time
import hashlib
import base64
import json


class Qa(object):
    URL = "http://openapi.xfyun.cn/v2/aiui"
    APP_ID = "5cc5623f"  # 你的APP ID
    API_KEY = "7e82cb5de9a79bd50be1a925995c7d37"  # 你的API_KEY
    AUE = "raw"
    AUTH_ID = "559f3654871292b240a4eac4b445ce4d"
    DATA_TYPE = "text"  # 明确处理类型 text文本/audio音频
    SAMPLE_RATE = "16000"
    SCENE = "main"  # 情景值
    RESULT_LEVEL = "complete"
    LAT = "23.16"  # 纬度
    LNG = "113.23"  # 经度
    FILE_PATH = "test.txt"  # 如需要从文本中读取,填写文本文件地址,每行为一个输入

    @staticmethod
    def build_header():
        cur_time = str(int(time.time()))
        param = dict()
        param["result_level"] = Qa.RESULT_LEVEL
        param["auth_id"] = Qa.AUTH_ID
        param["data_type"] = Qa.DATA_TYPE
        param["sample_rate"] = Qa.SAMPLE_RATE
        param["scene"] = Qa.SCENE
        param["lat"] = Qa.LAT
        param["lng"] = Qa.LNG
        param_content = json.dumps(param)
        param_base64 = base64.b64encode(param_content.encode('utf-8'))

        m2 = hashlib.md5()
        m2.update((Qa.API_KEY + cur_time + str(param_base64)).encode('utf-8'))
        check_sum = m2.hexdigest()

        header = {
            'X-CurTime': cur_time,
            'X-Param': param_base64,
            'X-Appid': Qa.APP_ID,
            'X-CheckSum': check_sum,
        }
        return header

    @staticmethod
    def read_file(file_path):
        bin_file = open(file_path, 'rb')
        data = bin_file.read()
        bin_file.close()
        return data

    @staticmethod
    def request2aiui(text):
        bin_text = text.encode('utf-8')
        r = requests.post(Qa.URL, headers=Qa.build_header(), data=bin_text)
        content = r.content
        json_resp = json.loads(content.decode('utf-8'))
        code = json_resp['code']
        if code == '0':
            return json_resp['data'][0]["intent"]['answer']['text']
        else:
            raise Exception(json_resp)
