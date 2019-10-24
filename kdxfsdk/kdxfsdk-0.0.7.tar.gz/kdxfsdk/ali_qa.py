#-*- coding: utf-8 -*-
import requests
import time
import hashlib
import base64
import json
from qiniu import Auth
from qiniu import BucketManager
from random import choice
import requests


class Qa(object):
    URL = "http://openapi.xfyun.cn/v2/aiui"
    AUE = "raw"
    AUTH_ID = "559f3654871292b240a4eac4b445ce4d"
    URL = "http://openapi.xfyun.cn/v2/aiui"
    AUE = "raw"
    DATA_TYPE = "text" # 明确处理类型 text文本/audio音频
    SAMPLE_RATE = "16000"
    SCENE = "main" # 情景值
    RESULT_LEVEL = "complete"
    LAT = "23.16" # 纬度
    LNG = "113.23" # 经度
    #个性化参数，需转义
    PERS_PARAM = "{\\\"auth_id\\\":\\\"2894c985bf8b1111c6728db79d3479ae\\\"}"
    FILE_PATH = "test.txt" # 如需要从文本中读取,填写文本文件地址,每行为一个输入

    def __init__(self):
        access_key = 'uxg5asAaPu2NoROTusFXrxGMJrN_-ZoLgm4nwj65'
        secret_key = 'ou1lvbO8PxBtOCSUtD09MRWwHx6aTyUViMtpQCRA'
        q = Auth(access_key, secret_key)
        bucket = BucketManager(q)
        bucket_name = 'lmxia'
        base_url = "http://pzvj368mo.bkt.clouddn.com/"
        # 前缀
        prefix = "kdxfsdk/license/qa"
        # 列举条目
        limit = 10
        # 列举出除'/'的所有文件以及以'/'为分隔的所有前缀
        delimiter = None
        # 标记
        marker = None
        ret, eof, info = bucket.list(bucket_name, prefix, marker, limit, delimiter)
        iat_item = choice(ret["items"])
        license_key = iat_item.get("key", "kdxfsdk/license/qa/lmxia.config")
        private_url = q.private_download_url(base_url + license_key, expires=3600)
        r = requests.get(private_url)
        license_info = r.json()
        self.APP_ID = license_info.get("APPID")
        self.API_KEY = license_info.get("APIKey")

    def buildHeader(self):
        curTime = str(int(time.time()))
        param = "{\"result_level\":\""+self.RESULT_LEVEL+"\",\"auth_id\":\""+self.AUTH_ID+"\",\"data_type\":\""+self.DATA_TYPE+"\",\"sample_rate\":\""+self.SAMPLE_RATE+"\",\"scene\":\""+self.SCENE+"\",\"lat\":\""+self.LAT+"\",\"lng\":\""+self.LNG+"\"}"
        paramBase64 = base64.b64encode(param.encode('utf-8'))

        m2 = hashlib.md5()
        m2.update((self.API_KEY + curTime + str(paramBase64, 'utf-8')).encode('utf-8'))
        checkSum = m2.hexdigest()

        # 在 Http Request Header 中配置以下参数用于授权认证
        header = {
            'X-CurTime': curTime,
            'X-Param': paramBase64,
            'X-Appid': self.APP_ID,
            'X-CheckSum': checkSum,
        }
        return header

    def readFile(self, filePath):
        binfile = open(filePath, 'rb')
        data = binfile.read()
        print('data in file:', data)
        return data

    def request2aiui(self, text):
        bintext = str.encode(text)
        r = requests.post(self.URL, headers=self.buildHeader(), data=bintext)
        content = r.content
        json_resp = json.loads(content.decode('utf-8'))
        code = json_resp['code']
        if code == '0':
            return json_resp['data'][0]['intent']['answer'].get('text')
        else:
            raise Exception(json_resp)


if __name__ == "__main__":
    try:
        test_text = u'今天的天气怎么样'
        qa = Qa()
        resp = qa.request2aiui(test_text)
        print(resp)
    except Exception as e:
        print(e.args)
