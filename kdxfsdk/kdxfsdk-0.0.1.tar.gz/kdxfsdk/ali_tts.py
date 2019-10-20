#-*- coding: utf-8 -*-

import requests
import time
import hashlib
import base64
import json


class Tts(object):
    URL = "http://api.xfyun.cn/v1/service/v1/tts"
    AUE = "raw"
    APPID = "5cc5623f"
    API_KEY = "e09decff4637be28af1fc159db665cf2"

    def __init__(self, text):
        self.text = text

    def _get_body(self):
        return {'text': self.text}

    @staticmethod
    def _write_file(file_name, content):
        with open(file_name, 'wb') as f:
            f.write(content)
        f.close()

    def _get_header(self):
        cur_time = str(int(time.time()))
        param = dict()
        param["aue"] = self.AUE
        param["auf"] = "audio/L16;rate=16000"
        param["voice_name"] = "xiaoyan"
        param["engine_type"] = "intp65"
        param_content = json.dumps(param)
        param_base64 = str(base64.b64encode(param_content.encode('utf-8')))

        m2 = hashlib.md5()
        m2.update((self.API_KEY + cur_time + param_base64).encode('utf-8'))

        check_sum = m2.hexdigest()
        header = {
            'X-CurTime': cur_time,
            'X-Param': param_base64,
            'X-Appid': self.APPID,
            'X-CheckSum': check_sum,
            'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
        }
        return header

    def make_speach(self):
        r = requests.post(self.URL, headers=self._get_header(), data=self._get_body())
        content_type = r.headers['Content-Type']
        if content_type == "audio/mpeg":
            sid = r.headers['sid']
            if self.AUE == "raw":
                self._write_file("./" + sid + ".wav", r.content)
            else:
                self._write_file("./" + "xiaoyan" + ".mp3", r.content)
            return "./" + sid + ".wav"
        else:
            print (r.text)
