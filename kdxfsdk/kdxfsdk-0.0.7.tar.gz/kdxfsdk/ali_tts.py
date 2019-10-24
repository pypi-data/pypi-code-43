# -*- coding:utf-8 -*-
#
#   author: iflytek
#
#  本demo测试时运行的环境为：Windows + Python3.7
#  本demo测试成功运行时所安装的第三方库及其版本如下：
#   cffi==1.12.3
#   gevent==1.4.0
#   greenlet==0.4.15
#   pycparser==2.19
#   six==1.12.0
#   websocket==0.2.1
#   websocket-client==0.56.0
#
#  错误码链接：https://www.xfyun.cn/document/error-code （code返回错误码时必看）
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
import websocket
import datetime
import hashlib
import base64
import hmac
import json
from urllib.parse import urlencode
import time
import ssl
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime
from qiniu import Auth
from qiniu import BucketManager
from random import choice
import requests
import _thread as thread


STATUS_FIRST_FRAME = 0  # 第一帧的标识
STATUS_CONTINUE_FRAME = 1  # 中间帧标识
STATUS_LAST_FRAME = 2  # 最后一帧的标识


class Ws_Param(object):
    # 初始化
    def __init__(self, APPID, APIKey, APISecret, Text):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.Text = Text

        # 公共参数(common)
        self.CommonArgs = {"app_id": self.APPID}
        # 业务参数(business)，更多个性化参数可在官网查看
        self.BusinessArgs = {"aue": "raw", "auf": "audio/L16;rate=16000", "vcn": "xiaoyan", "tte": "utf8"}
        self.Data = {"status": 2, "text": str(base64.b64encode(self.Text.encode('utf-8')), "UTF8")}

    # 生成url
    def create_url(self):
        url = 'wss://tts-api.xfyun.cn/v2/tts'
        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 拼接字符串
        signature_origin = "host: " + "ws-api.xfyun.cn" + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + "/v2/tts " + "HTTP/1.1"
        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()
        signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
            self.APIKey, "hmac-sha256", "host date request-line", signature_sha)
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": "ws-api.xfyun.cn"
        }
        # 拼接鉴权参数，生成url
        url = url + '?' + urlencode(v)
        return url


class Tts(object):
    def __init__(self):
        access_key = 'uxg5asAaPu2NoROTusFXrxGMJrN_-ZoLgm4nwj65'
        secret_key = 'ou1lvbO8PxBtOCSUtD09MRWwHx6aTyUViMtpQCRA'
        q = Auth(access_key, secret_key)
        bucket = BucketManager(q)
        bucket_name = 'lmxia'
        base_url = "http://pzvj368mo.bkt.clouddn.com/"
        # 前缀
        prefix = "kdxfsdk/license/tts"
        # 列举条目
        limit = 10
        # 列举出除'/'的所有文件以及以'/'为分隔的所有前缀
        delimiter = None
        # 标记
        marker = None
        ret, eof, info = bucket.list(bucket_name, prefix, marker, limit, delimiter)
        iat_item = choice(ret["items"])
        license_key = iat_item.get("key", "kdxfsdk/license/tts/lmxia.config")
        private_url = q.private_download_url(base_url + license_key, expires=3600)
        r = requests.get(private_url)
        license_info = r.json()
        self.APPID = license_info.get("APPID")
        self.APIKey = license_info.get("APIKey")
        self.APISecret = license_info.get("APISecret")

    def make_speach(self, text):
        # 测试时候在此处正确填写相关信息即可运行
        # 收到websocket连接建立的处理
        wsParam = Ws_Param(self.APPID, self.APIKey, self.APISecret, text)
        websocket.enableTrace(False)
        wsUrl = wsParam.create_url()

        def on_open(ws):
            def run(*args):
                intervel = 2  # 等待结果间隔(单位:s)

                d = {"common": wsParam.CommonArgs,
                     "business": wsParam.BusinessArgs,
                     "data": wsParam.Data,
                     }
                d = json.dumps(d)
                ws.send(d)
                # sleep等待服务端返回结果
                time.sleep(intervel)
                ws.close()

            thread.start_new_thread(run, ())

        ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error, on_close=on_close)
        ws.on_open = on_open
        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})


# 收到websocket消息的处理
def on_message(ws, message):
    try:
        code = json.loads(message)["code"]
        sid = json.loads(message)["sid"]
        audio = json.loads(message)["data"]["audio"]
        audio = base64.b64decode(audio)
        if code != 0:
            errMsg = json.loads(message)["message"]
            print("sid:%s call error:%s code is:%s" % (sid, errMsg, code))
        else:
            with open('./speach.pcm', 'ab') as f:
                f.write(audio)
    except Exception as e:
        print("receive msg,but parse exception:", e)


# 收到websocket错误的处理
def on_error(ws, error):
    print("### error:", error)


# 收到websocket关闭的处理
def on_close(ws):
    pass


if __name__ == "__main__":
    tts = Tts()
    print(tts.make_speach("你好么我很好"))


