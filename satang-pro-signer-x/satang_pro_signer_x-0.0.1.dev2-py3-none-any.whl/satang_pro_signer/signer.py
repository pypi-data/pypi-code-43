import hashlib
import hmac

from satang_pro_signer import preparer

class Signer:
    def __init__(self, secret: bytes):
        self.secret = secret

    def sign(self, obj) -> bytes:

        parsed = preparer.Preparer(obj).encode()
        msg = bytes(parsed, encoding='utf-8')

        try:
            # better performance
            return hmac.digest(self.secret, msg, 'sha512')
        except AttributeError:
            # compatible with Python 3.6
            m = hmac.new(self.secret, msg, hashlib.sha512)
            return m.digest()