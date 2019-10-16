# coding:utf-8
"""
云从是付费接口, 身份证识别是 1 分 1 次。
"""

import base64
import hashlib
import hmac
from typing import Dict, Any, Optional
from urllib.parse import urljoin

import requests
from nezha.ustring import to_bytes, to_str

__all__ = ('CloudWalkOCRBase')


def get_authorization(sk: str, msg: str) -> bytes:
    k = to_bytes(sk)
    m = to_bytes(msg)
    hashing = hmac.new(k, m, digestmod=hashlib.sha1).digest()
    return hashing


class CloudWalkOCRBase:
    f_data = 'data'
    f_code = 'code'
    # 这些状态码不收费，可视为接口异常；
    system_error_code = [20000001,
                         20000002,
                         20000003,
                         20000004,
                         20000005,
                         20000006,
                         20000007,
                         20000008,
                         20000009,
                         20000010,
                         20001040,
                         20001041,
                         80045005,
                         80050000,
                         80050002, ]

    def __init__(self, app_key: str, app_secret: str, uri: str, host: str):
        self.app_key: str = app_key
        self.app_secret: str = app_secret
        self.uri: str = uri
        self.host: str = host
        self.url: str = urljoin(host, uri)
        self.send_data: Dict = dict()

    @property
    def cls_name(self) -> str:
        return CloudWalkOCRBase.__name__

    def generate_sign(self, send_data: Dict[str, Any]) -> str:
        """
        云从加密时的坑，uri 必须以 / 开头，否则会加密失败;
        :param send_data:
        :return:
        """
        if not isinstance(send_data, dict):
            raise TypeError(u'send_data {} type {} should be dict'.format(send_data, type(send_data)))
        a = send_data.copy()
        print('self.uri', self.uri)
        a['uri'] = self.uri if self.uri.startswith('/') else '/' + self.uri
        auth_info = u"&".join(u"{}={}".format(i, a[i]) for i in sorted(a))
        code = get_authorization(self.app_secret, auth_info)
        return to_str(base64.b64encode(code))

    def request(self, send_data: Dict[str, Any] = None) -> Dict[str, Any]:
        send_data = send_data or self.send_data
        response = requests.post(self.url, json=send_data)
        if not response.ok:
            raise ValueError(u'{} response.status_code is {}'.format(self.cls_name, response.status_code))
        resp = response.json()
        if not isinstance(resp, dict):
            raise ValueError("resp {} type {} not dict".format(resp, type(resp)))
        if resp.get('code', None) is None:
            raise ValueError("resp {} code {} is None".format(resp, resp.get('code', None)))
        resp_code = int(resp['code'])
        if resp_code not in self.system_error_code:
            return resp
        else:
            raise ValueError(u"{} resp {} is unexpected".format(self.cls_name, response.text))

    @classmethod
    def get_response_body(cls, resp: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return resp.get(cls.f_data)

    @classmethod
    def get_code(cls, resp: Dict[str, Any]) -> Optional[str]:
        return resp.get(cls.f_code)

    def generate_send_data(self, img: str) -> Dict[str, str]:
        raise NotImplementedError()

    def set_send_data(self, img: str) -> 'CloudWalkOCRBase':
        self.send_data = self.generate_send_data(img)
        return self
