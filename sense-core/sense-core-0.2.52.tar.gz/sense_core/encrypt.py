import base64
from Crypto.Cipher import AES

'''
采用AES对称加密算法
'''


class Encryption(object):

    sk = 'sdf8g4edf809p2fssdai'

    @classmethod
    def __add_to_16(cls, value):
        while len(value) % 16 != 0:
            value += '\0'
        return str.encode(value)

    @classmethod
    def encrypt_key(cls, key):
        aes = AES.new(cls.__add_to_16(cls.sk), AES.MODE_ECB)
        encrypt_aes = aes.encrypt(cls.__add_to_16(key))
        encrypted_text = str(base64.encodebytes(encrypt_aes), encoding='utf-8')  # 执行加密并转码返回bytes
        if encrypted_text.endswith('\n'):
            encrypted_text = encrypted_text.split('\n')[0]
        return encrypted_text

    @classmethod
    def decrypt_key(cls, key):
        aes = AES.new(cls.__add_to_16(cls.sk), AES.MODE_ECB)
        base64_decrypted = base64.decodebytes(key.encode(encoding='utf-8'))
        decrypted_text = str(aes.decrypt(base64_decrypted), encoding='utf-8').replace('\0', '')
        return decrypted_text

    @classmethod
    def encryt_dict(cls, config_map, ignore=None):
        # ignore 为忽略的字段，默认值是none，值为list，如['a', 'b']
        _res = {}
        for _k, _v in config_map.items():
            if ignore and _k in ignore:
                _res[_k] = _v
                continue
            _res[_k] = cls.encrypt_key(_v)
        return _res

    @classmethod
    def decrypt_dict(cls, config_map, ignore=None):
        # ignore 为忽略的字段，默认值是none，值为list，如['a', 'b']
        _res = {}
        for _k, _v in config_map.items():
            if ignore and _k in ignore:
                _res[_k] = _v
                continue
            try:
                _res[_k] = cls.decrypt_key(_v)
            except:
                _res[_k] = _v
        return _res