import re
import random
import string
import hashlib
import base64
import functools
from . import strutils

def get_hash_hexdigest(*args, method=hashlib.md5):
    data = "".join(map(str, args)).encode("utf-8")
    gen = method(data)
    return gen.hexdigest()

get_md5 = get_md5_hexdigest = functools.partial(get_hash_hexdigest, method=hashlib.md5)
get_sha1 = get_sha1_hexdigest = functools.partial(get_hash_hexdigest, method=hashlib.sha1)
get_sha256 = get_sha256_hexdigest = functools.partial(get_hash_hexdigest, method=hashlib.sha256)

def get_hash_base64(*args, method=hashlib.md5):
    data = "".join(map(str, args)).encode("utf-8")
    gen = method(data)
    data = gen.digest()
    text = base64.encodebytes(data).decode()
    return strutils.join_lines(text)

get_md5_base64 = functools.partial(get_hash_base64, method=hashlib.md5)
get_sha1_base64 = functools.partial(get_hash_base64, method=hashlib.sha1)
get_sha256_base64 = functools.partial(get_hash_base64, method=hashlib.sha256)


def get_pbkdf2_hmac(text, salt=None, iterations=150000, hash_name="sha256"):
    if salt is None:
        salt = "".join(random.choices(string.ascii_letters, k=16))
    data = hashlib.pbkdf2_hmac(hash_name, text.encode("utf-8"), salt.encode("utf-8"), iterations)
    return "pbkdf2_{hash_name}${iterations}${salt}${data}".format(
        hash_name=hash_name,
        iterations=iterations,
        salt=salt,
        data=strutils.join_lines(base64.encodebytes(data).decode()),
    )

def validate_pbkdf2_hmac(password, text):
    matches = re.findall(r"pbkdf2_(.+)\$(\d+)\$(.+)\$(.+)", text)
    if len(matches) != 1:
        return False
    hash_name, iterations, salt, _ = matches[0]
    if not iterations.isdigit():
        return False
    else:
        iterations = int(iterations)
    data = get_pbkdf2_hmac(password, salt=salt, iterations=iterations, hash_name=hash_name)
    if data == text:
        return True
    else:
        return False

get_pbkdf2_sha256 = functools.partial(get_pbkdf2_hmac, hash_name="sha256")
validate_pbkdf2_sha256 = validate_pbkdf2_hmac

get_pbkdf2_sha1 = functools.partial(get_pbkdf2_hmac, hash_name="sha1")
validate_pbkdf2_sha1 = validate_pbkdf2_hmac

get_pbkdf2_md5 = functools.partial(get_pbkdf2_hmac, hash_name="md5")
validate_pbkdf2_md5 = validate_pbkdf2_hmac
