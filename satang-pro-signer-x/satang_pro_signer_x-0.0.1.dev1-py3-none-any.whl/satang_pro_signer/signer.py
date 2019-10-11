import hashlib
import hmac

from satang_pro_signer import preparer

class Signer:
    def __init__(self, secret: bytes):
        self.secret = secret

    def sign(self, obj) -> bytes:
        parsed = preparer.PreparerFactory().get_preparer(obj).parse()
        msg = bytes(parsed, encoding='utf-8')

        mac = hmac.new(self.secret, digestmod=hashlib.sha512)
        mac.update(msg)

        return mac.digest()