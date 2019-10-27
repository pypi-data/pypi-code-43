from iot_message.abstract.cryptor_interface import CryptorInterface
from Crypto.Cipher import AES
from Crypto.Hash import SHA, HMAC
import iot_message.exception as ex
import binascii
from Crypto import Random
import json


class Cryptor(CryptorInterface):
    name = "message.aessha1"
    algorithm = AES.MODE_CBC

    def __init__(self, staticiv, ivkey, datakey, passphrase):
        self.staticiv = staticiv
        self.ivkey = ivkey
        self.datakey = datakey
        self.passphrase = passphrase

    def encrypt(self, message):
        msg = json.dumps(message.data)
        msg_pad = _pad(16, msg)
        iv = Random.new().read(AES.block_size)
        iv = binascii.hexlify(iv)[:16]
        iv_suite = AES.new(self.ivkey.encode(), AES.MODE_CBC, self.staticiv.encode())
        encrypted_iv = iv_suite.encrypt(iv)

        data_suite = AES.new(self.datakey.encode(), AES.MODE_CBC, iv)
        encrypted_data = data_suite.encrypt(msg_pad.encode())

        fullmessage = iv.decode('utf8') + msg
        hmac = HMAC.new(self.passphrase.encode(), fullmessage.encode(), SHA)
        computed_hash = hmac.hexdigest()

        message.set({
            'event': self.name,
            'parameters': [
                binascii.hexlify(encrypted_iv).decode('utf8'),
                binascii.hexlify(encrypted_data).decode('utf8'),
                computed_hash
            ],
            'response': ''
        })

    def decrypt(self, message):
        encrypted_iv = binascii.unhexlify(message.data['parameters'][0])
        encrypted_data = binascii.unhexlify(message.data['parameters'][1])
        _hash = message.data['parameters'][2]

        iv_suite = AES.new(self.ivkey.encode(), self.algorithm, self.staticiv.encode())
        iv = iv_suite.decrypt(encrypted_iv)
        data_suite = AES.new(self.datakey.encode(), self.algorithm, iv)
        data = data_suite.decrypt(encrypted_data).strip(b'\x00').decode('utf8')
        fullmessage = iv.decode('utf8') + data
        hmac = HMAC.new(self.passphrase.encode(), fullmessage.encode(), SHA)
        try:
            hmac.verify(binascii.unhexlify(_hash))
        except ValueError as e:
            raise ex.HmacException(hmac.hexdigest(), _hash)

        msg = json.loads(data)
        message.clear()
        message.set(msg)


def _pad(l, s):
    return s + (l - len(s) % l) * chr(00)
