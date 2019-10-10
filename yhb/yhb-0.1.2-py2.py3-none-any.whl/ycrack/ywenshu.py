import math
import json
import base64
import random
import requests

from datetime import datetime
from Cryptodome.Cipher import DES3
from Cryptodome.Util.Padding import pad, unpad


class Token(str):
    def __new__(cls, size: int):
        arr = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        string = "".join(arr[round(random.random() * (len(arr) - 1))] for _ in range(size))
        return super(Token, cls).__new__(cls, string)


class PID(str):
    def __new__(cls):
        page_id = "".join(hex(math.floor(random.random() * 16))[2:] for _ in range(32))
        return super(PID, cls).__new__(cls, page_id)


def d3_encrypt(plain_text: str, key: str, iv: str) -> str:
    des3 = DES3.new(key=key.encode(), mode=DES3.MODE_CBC, iv=iv.encode())
    encrypted_data = des3.encrypt(pad(plain_text.encode(), DES3.block_size))
    cipher_text = base64.b64encode(encrypted_data).decode()
    return cipher_text


def d3_decrypt(cipher_text: str, key: str, iv: str) -> str:
    des3 = DES3.new(key=key.encode(), mode=DES3.MODE_CBC, iv=iv.encode())
    decrypted_data = des3.decrypt(base64.b64decode(cipher_text))
    plain_text = unpad(decrypted_data, DES3.block_size).decode()
    return plain_text


class CipherText(str):
    def __new__(cls):
        return cls.cipher()

    @classmethod
    def cipher(cls) -> str:
        date = datetime.now()
        timestamp = str(int(date.timestamp() * 1000))
        salt = Token(24)
        iv = date.strftime("%Y%m%d")

        enc = d3_encrypt(plain_text=timestamp, key=salt, iv=iv)
        cipher_text = cls.str2binary(salt + iv + enc)

        return super(CipherText, cls).__new__(cls, cipher_text)

    @staticmethod
    def str2binary(string: str) -> str:
        return " ".join(bin(ord(item))[2:] for item in string)


class WenshuCrack(object):
    url = "http://wenshu.court.gov.cn/website/parse/rest.q4w"

    def __init__(self, headers=None, proxies=None, timeout=20):
        self.timeout = timeout
        self.session = requests.Session()

        if headers is None:
            self.session.headers.update({
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 "
                              "(KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36",
            })
        else:
            self.session.headers.update(headers)

        self.session.proxies = proxies

    def _request(self, data: dict) -> requests.Response:
        response = self.session.post(self.url, data=data, timeout=self.timeout)
        if response.status_code != 200:
            raise Exception(response.status_code)
        json_data = response.json()
        plain_text = d3_decrypt(cipher_text=json_data["result"],
                                key=json_data["secretKey"],
                                iv=datetime.now().strftime("%Y%m%d"))
        result = json.loads(plain_text)
        return result

    def list_page(self, page_num=1, page_size=5, query_condition=None):
        assert isinstance(page_num, int)
        assert isinstance(page_size, int)
        assert query_condition is not None
        data = {
            "pageId": PID(),
            "sortFields": "s50:desc",
            "ciphertext": CipherText(),
            "pageNum": page_num,
            "pageSize": page_size,
            "queryCondition": query_condition,
            "cfg": "com.lawyee.judge.dc.parse.dto.SearchDataDsoDTO@queryDoc",
            "__RequestVerificationToken": Token(24),
        }

        result = self._request(data)
        return result

    def detail_page(self, docid):
        assert isinstance(docid, str)
        assert len(docid) == 32
        data = {
            "docId": docid,
            "ciphertext": CipherText(),
            "cfg": "com.lawyee.judge.dc.parse.dto.SearchDataDsoDTO@docInfoSearch",
            "__RequestVerificationToken": Token(24),
        }

        result = self._request(data)
        return result


if __name__ == '__main__':
    wc = WenshuCrack()
    print(wc.list_page(1, 5, json.dumps([{"key": "s8", "value": "03"}])))
    print(wc.detail_page('e5e85a4d0b3346219acdaabf00c110db'))
