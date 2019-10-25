import hashlib
from base64 import b64encode, b64decode

from functools import partial


def textmd5sum(text):
    md5sum = hashlib.md5()
    hash_seed = text.encode('utf-8')
    md5sum.update(hash_seed)
    md5string = str(md5sum.hexdigest())
    return md5string


def textsha256(text):
    sha256 = hashlib.sha256()
    sha256.update(text.encode('utf-8'))
    return str(sha256.hexdigest())


def filemsha256(file_path):
    with open(file_path, 'rb') as file_handler:
        sha256 = hashlib.sha256()
        for part in iter(partial(file_handler.read, 128), b''):
            sha256.update(part)
    return sha256.hexdigest()


def filemd5sum(file_path):
    with open(file_path, 'rb') as file_handler:
        md5sum = hashlib.md5()
        for part in iter(partial(file_handler.read, 128), b''):
            md5sum.update(part)
    return md5sum.hexdigest()


def base64(text):
    return b64encode(text)


def base64decode(text):
    return b64decode(text)
