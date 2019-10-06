#!usr/bin/env python
#-*- coding:utf-8 _*-
"""
@file: encrypt.py
@time: 2019/04/09
"""

import hashlib,base64

def md5_encrypt(text,salt=''):
    '''
    md5加密
    :param text:  加密文本
    :param salt:  盐
    :return:
    '''
    return hashlib.md5((text+salt).encode('utf-8')).hexdigest()

def base64_encrypt(text):
    '''
    base64加密
    :param text:  加密文本
    :return:
    '''

    return (base64.b64encode(text.encode('utf-8'))).decode('utf-8')

def base64_decrypt(text):
    '''
    base64解密
    :param text:
    :return:
    '''
    return (base64.b64decode(text.encode('utf-8'))).decode('utf-8')


if __name__ == '__main__':
    print(base64_encrypt("11111"))
    print(base64_decrypt("MTExMTE="))
    print(md5_encrypt('11111','abc'))

