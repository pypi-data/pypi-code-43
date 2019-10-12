# -*- coding: utf-8 -*-
# @Time     : 2019/10/10 8:47
# @Author   : Run 
# @File     : cipher.py
# @Software : PyCharm

"""
todo figure out how to make codes more concise
Notes:
    1. 中文字符在不同编码下的值不同，md5加密后的结果也不同。
    2. AES, python2 `pycrypto`; python3 `pycryptodome` todo
"""


import hashlib
import os
import codecs


def bytes_to_str16(bs: bytes) -> str:
    """字节码 -> 16进制字符串"""
    return codecs.encode(bs, 'hex').decode()


def str16_to_bytes(str16: str) -> bytes:
    """16进制字符串 -> 字节码"""
    # return bytearray.fromhex(str16)
    return codecs.decode(str16.encode(), 'hex')


def get_str_md5(s: 'str or bytes'):
    if isinstance(s, bytes):
        pass
    elif isinstance(s, str):
        s = s.encode()
    else:
        raise Exception("please check the type of your input")
        # return "please check the type of your input"

    return hashlib.md5(s).hexdigest()


def get_file_md5(file_name, chunk_size=10240):
    m = hashlib.md5()
    if os.path.isfile(file_name):
        with open(file_name, 'rb') as file:
            while True:
                data = file.read(chunk_size)
                if not data: break
                m.update(data)
        return m.hexdigest()
    else:
        # return "file doesn't exsit"
        raise Exception("file doesn't exsit")


MD5_HEX_COLLISION = [
    (
        'd131dd02c5e6eec4693d9a0698aff95c2fcab58712467eab4004583eb8fb7f89'
        '55ad340609f4b30283e488832571415a085125e8f7cdc99fd91dbdf280373c5b'
        'd8823e3156348f5bae6dacd436c919c6dd53e2b487da03fd02396306d248cda0'
        'e99f33420f577ee8ce54b67080a80d1ec69821bcb6a8839396f9652b6ff72a70',
        'd131dd02c5e6eec4693d9a0698aff95c2fcab50712467eab4004583eb8fb7f89'
        '55ad340609f4b30283e4888325f1415a085125e8f7cdc99fd91dbd7280373c5b'
        'd8823e3156348f5bae6dacd436c919c6dd53e23487da03fd02396306d248cda0'
        'e99f33420f577ee8ce54b67080280d1ec69821bcb6a8839396f965ab6ff72a70'
    ),
    (
        '4dc968ff0ee35c209572d4777b721587d36fa7b21bdc56b74a3dc0783e7b9518'
        'afbfa200a8284bf36e8e4b55b35f427593d849676da0d1555d8360fb5f07fea2',
        '4dc968ff0ee35c209572d4777b721587d36fa7b21bdc56b74a3dc0783e7b9518'
        'afbfa202a8284bf36e8e4b55b35f427593d849676da0d1d55d8360fb5f07fea2'
    ),
    (
        '0e306561559aa787d00bc6f70bbdfe3404cf03659e704f8534c00ffb659c4c87'
        '40cc942feb2da115a3f4155cbb8607497386656d7d1f34a42059d78f5a8dd1ef',
        '0e306561559aa787d00bc6f70bbdfe3404cf03659e744f8534c00ffb659c4c87'
        '40cc942feb2da115a3f415dcbb8607497386656d7d1f34a42059d78f5a8dd1ef'
    )
]


def get_str_sha1(s: 'str or bytes'):
    if isinstance(s, bytes):
        pass
    elif isinstance(s, str):
        s = s.encode()
    else:
        raise Exception("please check the type of your input")
        # return "please check the type of your input"

    return hashlib.sha1(s).hexdigest()


def get_file_sha1(file_name, chunk_size=10240):
    m = hashlib.sha1()
    if os.path.isfile(file_name):
        with open(file_name, 'rb') as file:
            while True:
                data = file.read(chunk_size)
                if not data: break
                m.update(data)
        return m.hexdigest()
    else:
        # return "file doesn't exsit"
        raise Exception("file doesn't exsit")


def get_str_sha256(s: 'str or bytes'):
    if isinstance(s, bytes):
        pass
    elif isinstance(s, str):
        s = s.encode()
    else:
        raise Exception("please check the type of your input")
        # return "please check the type of your input"

    return hashlib.sha256(s).hexdigest()


def get_file_sha256(file_name, chunk_size=10240):
    m = hashlib.sha256()
    if os.path.isfile(file_name):
        with open(file_name, 'rb') as file:
            while True:
                data = file.read(chunk_size)
                if not data: break
                m.update(data)
        return m.hexdigest()
    else:
        # return "file doesn't exsit"
        raise Exception("file doesn't exsit")


if __name__ == "__main__":
    print(bytes_to_str16(b'\xe4\xb8\xad'))
    print(str16_to_bytes('e4b8ad'))
    print()

    for s1, s2 in MD5_HEX_COLLISION:
        print(s1 == s2, str16_to_bytes(s1) == str16_to_bytes(s2),
              get_str_md5(str16_to_bytes(s1)) == get_str_md5(str16_to_bytes(s2)))