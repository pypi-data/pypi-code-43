import json
import time
from typing import Dict, Any, Union

import requests
from Crypto.Hash import SHA
from nezha.encryption.des import DES
from nezha.encryption.rsa2 import RSAEncryption
from nezha.ustring import unique_id


class SuixingfuBase:

    def __init__(self, des_key: str, rsa_prv_key: str, url: str, channel_number: str):
        self.des_key: str = des_key
        self.rsa_prv_key: str = rsa_prv_key
        self.url: str = url
        self.channel_number: str = channel_number
        self.biz_data: Dict = dict()

    def generate_sign(self, send_data: Dict[str, str]) -> Union[str, bytes]:
        """
        对Base64编码后的reqData密文使用合作方RSA私钥进行签名，
        将签名结果用Base64编码后得到签名串，将签名串放置到报文头的sign字段中，请求报文构造完成发送。
        sign=$(self.reqData -> RSA私钥进行签名 -> Base64编码)
        :return:
        """
        return RSAEncryption.generate_signature(self.generate_req_data(send_data)['reqData'], self.rsa_prv_key,
                                                hash_type=SHA)

    def generate_order_num(self) -> str:
        return str(unique_id())

    def generate_header(self, sign: str, order_num: str, timestamp: str = time.strftime('%Y%m%d%H%M%S')) -> Dict[
        str, str]:
        return dict(
            channelNo=self.channel_number,
            orderNo=order_num,
            sign=sign,
            timeStamp=timestamp,
        )

    def generate_req_data(self, send_data: Dict[str, Any]) -> Dict[str, str]:
        jsonify = json.dumps(send_data)
        req_data = DES.encrypt(jsonify, self.des_key)
        if not isinstance(req_data, str):
            raise TypeError(f'unexpected type {req_data} {type(req_data)}')
        return {
            'reqData': req_data
        }

    def _request(self, send_data: Dict[str, str], header: Dict[str, str]) -> Dict[str, str]:
        """
        注意 headers 和传值方式，和随行付文档中的完全不一致；
        :param orderNo: 请求订单号, 每次请求必须是唯一值，标明此报文的唯一编号
        :return:
        """
        response = requests.post(self.url, headers=header, data=send_data)
        if not response.ok:
            raise ValueError(
                f'response.content {response.content} response.status_code {response.status_code} is invalid')
        return response.json()

    def request(self, biz_data: Dict[str, str]) -> Dict[str, str]:
        biz_data = biz_data or self.biz_data
        req_data = self.generate_req_data(biz_data)
        sign = self.generate_sign(biz_data)
        order_num = self.generate_order_num()
        if not isinstance(sign, str):
            raise TypeError(f'unexpected sign {sign} type {type(sign)}')
        header = self.generate_header(sign, order_num)
        return self._request(req_data, header)

    # def generate_biz_data(self, *args: str) -> Dict[str, str]:
    #     raise NotImplementedError()
