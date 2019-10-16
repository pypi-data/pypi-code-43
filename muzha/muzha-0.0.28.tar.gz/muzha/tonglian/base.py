from typing import Dict, Any

import requests
from nezha.hash import hash_md5
from nezha.url import urlencode
from nezha.utime import strftime, NO_BLANK_FMT


class TonglianBase:

    def __init__(self, url: str, key: str, appid: str, cusid: str, version: str, randomstr: str,
                 timeStamp: str = strftime(fmt=NO_BLANK_FMT)):
        self.url = url
        self.key = key
        self.appid = appid
        self.cusid = cusid
        self.version = version
        self.timeStamp = timeStamp
        self.randomstr = randomstr

    @staticmethod
    def generate_sign(biz_data: Dict[str, Any], key: str) -> str:
        """
        构造请求中的 reqData
        reqData=$(
        原始数据 -->加sign(
            md5(所有参与签名的字段，按字段名的ASCLL码从小到大排序后，使用URL的键值对的格式
            (即key1=value1&key2=value2)拼接成字符串string,另外string中包含key即appkey字段)
            )
        )
        :return:
        """
        base_req_data = biz_data.copy()
        base_req_data['key'] = key
        sorted_str = urlencode(base_req_data, safe=False, sorted_by_ascii=True)
        return hash_md5(sorted_str)

    def generate_req_data(self, biz_data: Dict[str, Any]) -> Dict[str, Any]:
        base_req_data = {
            'appid': self.appid,
            'cusid': self.cusid,
            'version': self.version,
            'timestamp': self.timeStamp,
            'randomstr': self.randomstr,
        }
        base_req_data.update(biz_data)
        base_req_data['sign'] = self.generate_sign(base_req_data, self.key)
        return base_req_data

    def _request(self, req_data: Dict[str, Any]) -> Dict[str, Any]:
        r = requests.post(self.url, data=req_data)
        # 记录日志, 表明调通联的接口不通
        if not r.ok:
            raise ValueError(f'TongLianServiceCode {r.text} {r.status_code}')
        return r.json()

    def request(self, biz_data: Dict[str, Any]) -> Dict[str, Any]:
        req_data = self.generate_req_data(biz_data)
        return self._request(req_data)
