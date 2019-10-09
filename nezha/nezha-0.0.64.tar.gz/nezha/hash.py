import base64
import hashlib
import hmac
from typing import Union, Callable

from nezha.ustring import to_bytes, to_str


def hash_hmac(key: Union[str, bytes],
              plaintext: Union[str, bytes],
              digestmod: Callable = hashlib.sha1,
              returned_str: bool = True,
              returned_base64: bool = False) -> Union[str, bytes]:
    obj = hmac.new(to_bytes(key), to_bytes(plaintext), digestmod=digestmod)
    if returned_base64:
        return to_str(base64.b64encode(obj.digest()))
    if returned_str:
        return obj.hexdigest()
    else:
        return obj.digest()


def hash_hmac_currying(key: Union[str, bytes]) -> Callable:
    def wrap(plaintext: Union[str, bytes],
             digestmod: Callable = hashlib.sha1,
             returned_str: bool = True,
             returned_base64: bool = False) -> Union[str, bytes]:
        return hash_hmac(key, plaintext, digestmod=digestmod,
                         returned_str=returned_str, returned_base64=returned_base64)

    return wrap


def hash_md5(plaintext: Union[str, bytes], key: Union[str, bytes] = '') -> str:
    text = to_str(plaintext) + to_str(key)
    m = hashlib.md5()
    m.update(to_bytes(text))
    return m.hexdigest()
