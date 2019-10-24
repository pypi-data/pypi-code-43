import base64
import hashlib
from Crypto.Cipher import AES


class Encryption(object):

    def __init__(self, key, iv_):
        self.byte_string = 16
        self.key = hashlib.sha256(key.encode()).hexdigest()[:32]
        self.iv = hashlib.sha256(iv_.encode()).hexdigest()[:16]

    def encrypt(self, raw):
        """
        Encrypt passed json data with the secret key,iv key.
        """
        cipher = AES.new(self.key.encode('utf-8'), AES.MODE_CBC, self.iv.encode('utf-8'))
        crypt = cipher.encrypt(self._pad(raw).encode())
        return base64.b64encode(base64.b64encode(crypt)).decode('utf-8')

    def _pad(self, s):
        return s + (self.byte_string - len(s) % self.byte_string) * chr(self.byte_string - len(s) % self.byte_string)

    @staticmethod
    def _un_pad(s):
        return s[:-ord(s[len(s) - 1:])]