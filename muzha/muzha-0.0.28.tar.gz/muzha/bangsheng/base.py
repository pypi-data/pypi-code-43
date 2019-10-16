import hashlib
from typing import Dict, Any
from urllib.parse import urlencode
from urllib.parse import urljoin

import requests
from nezha.errors import IncomingDataError
from nezha import udict
from nezha import url
from nezha.hash import hash_hmac
from nezha.utime import timestamp


class BangShengBase:
    u"""
    邦盛接口管理, 它有请求邦盛接口和解析邦盛接口返回值的能力
    邦盛接口有 ip白名单 限制，本地调不通的;
    接口传入的时间与标准时间差15分钟以上，抛出异常：{"code":1016,"message":"Unauthorized","status":401}
    参数异常，{"code":1010,"message":"parameters verify error","status":400}
    之前的接口, 业务码都是在 json 中判断；
    但是邦盛的接口，如果参数错误则直接 400 了。
    在邦盛的测试环境，参数错误和时间限制，这两个异常都测试不出来;
    """

    def __init__(self, host: str, uri: str, app_key: str, app_secret: str):
        self.host: str = host
        self.uri: str = uri
        self.url: str = urljoin(self.host, self.uri)
        self.app_key: str = app_key
        self.app_secret: str = app_secret
        self.date: str = str(timestamp(precision='ms', returned_str=True))
        self.full_url: str = ''
        self.header: Dict = dict()
        self.biz_data: Dict[str, str] = dict()

    def generate_full_url(self, biz_data: Dict[str, Any]) -> str:
        u"""
        request 请求的 url, 映射 demo 中的 httpget
        原始逻辑：url + urlPath + "?" + encodeParam
        url 接口地址 + urlPath api 地址 + '?' + 转码后的参数
        :return: str
        """
        return '?'.join((self.url, urlencode(biz_data)))

    def set_full_url(self, biz_data: Dict[str, Any] = None) -> 'BangShengBase':
        biz_data = biz_data or self.biz_data
        self.full_url = self.generate_full_url(biz_data)
        return self

    def generate_sign(self, biz_data: Dict[str, Any]) -> str:
        u"""
        请求中 header 头部的 X-BS-Validate 对应的值
        代码逻辑：
        String validate = HmacUtils.hmacMd5Hex(
            APP_SECRET.getBytes(), signString.getBytes(Charset.forName("UTF-8")));
        :return: str
        """
        joined_uri = url.urlencode(biz_data, safe=False)
        raw_sign = '\n'.join((self.uri, joined_uri, self.date))
        encrypted =  hash_hmac(self.app_secret, raw_sign, digestmod=hashlib.md5)
        if not isinstance(encrypted, str):
            raise TypeError(f'unexpected encrypted {encrypted} type {type(encrypted)}')
        return encrypted

    def generate_header(self, biz_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'X-BS-App-Key': self.app_key,
            'X-BS-Date': self.date,
            'X-BS-Validate': self.generate_sign(biz_data),
        }

    def set_header(self, biz_data: Dict[str, Any] = None) -> 'BangShengBase':
        biz_data = biz_data or self.biz_data
        self.header = self.generate_header(biz_data)
        return self

    @staticmethod
    def generate_biz_data(name: str = '', mobile: str = '', idCard: str = '') -> Dict[str, str]:
        return udict.Dict.filter(locals())

    def set_biz_data(self, name: str, mobile: str, idCard: str) -> 'BangShengBase':
        self.biz_data = self.generate_biz_data(name=name, mobile=mobile, idCard=idCard)
        return self

    def request(self, full_url: str = '', headers: Dict[str, str] = None) -> Dict[str, str]:
        u"""
        请求邦盛的接口
        encourage chain operation:
        BangShengBase().set_biz_data().set_full_url().set_header().request()
        """
        full_url = full_url or self.full_url
        headers = headers or self.header
        response = requests.get(full_url, headers=headers)
        if response.ok:
            return response.json()
        elif response.status_code == requests.codes['bad_request']:
            code = response.json().get('code')
            if code == 1010:
                raise IncomingDataError(f'text {response.text} code {code} is unexpected')
            else:
                raise ValueError(f'text {response.text} code {code} is unexpected')
        else:
            raise ValueError(f'text {response.text} and status_code {response.status_code} is unexpected')
