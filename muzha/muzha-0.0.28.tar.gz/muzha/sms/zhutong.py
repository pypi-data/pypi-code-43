# 实现助通云通信接口
# -*- coding: utf8 -*-

import requests

from nezha.hash import hash_md5
from nezha.utime import strftime


class SMS:

    def __init__(self, username: str, raw_password: str):
        self.username: str = username
        self.password: str = raw_password
        self.tKey: str = strftime()
        self.encrypted_password: str = self.encrypt_sms_password(self.password, self.tKey)

    @staticmethod
    def encrypt_sms_password(password: str, tKey: str) -> str:
        return hash_md5(hash_md5(password), key=tKey)

    def send_sms(self, mobile: str, content: str, send_sms_url: str, time: str = '') -> bool:
        """
        普通短信单群发接口
        """
        values = {"username": self.username,
                  "mobile": mobile,
                  "content": content,
                  "tKey": self.tKey,
                  "password": self.encrypted_password,
                  "time": time,
                  }
        response = requests.post(url=send_sms_url, json=values)
        if response.ok:
            return response.json().get('code') == 200
        else:
            raise Exception('response {}'.format(response.text))

    def get_sms_balance(self, balance_sms_url: str) -> int:
        """
        获取助通短信剩余条数
        :return:
        """
        values = {"username": self.username,
                  "tKey": self.tKey,
                  "password": self.encrypted_password,
                  }
        resp = requests.post(url=balance_sms_url, json=values)
        if resp.ok:
            sum_sms = resp.json()['sumSms']
            if sum_sms is None:
                raise Exception('sum_sms is None')
            return int(sum_sms)
        else:
            raise Exception('resp status code {} is invalid, resp.text {}'.format(resp.status_code, resp.text))
