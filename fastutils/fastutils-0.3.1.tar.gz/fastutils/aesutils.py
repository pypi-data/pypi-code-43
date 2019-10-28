import os
import hashlib
import binascii
import base64
from Crypto.Cipher import AES
from . import strutils

AES_BLOCK_SIZE = AES.block_size
 

def get_sha1prng_key(key):
    """
    encrypt key with SHA1PRNG
    same as java AES crypto key generator SHA1PRNG
    """
    signature = hashlib.sha1(key.encode()).digest()
    signature = hashlib.sha1(signature).digest()
    return signature[:16]

def get_md5_key(key):
    signature = hashlib.md5(key.encode()).digest()
    return signature

def padding_ansix923(value):
    padsize = AES.block_size - len(value) % AES.block_size
    return value + bytes([0] * (padsize -1)) + bytes([padsize])

def remove_padding_ansix923(value):
    padsize = value[-1]
    return value[:-1*padsize]

def padding_iso10126(value):
    padsize = AES.block_size - len(value) % AES.block_size
    return value + os.urandom(padsize-1) + bytes([padsize])

def remove_padding_iso10126(value):
    padsize = value[-1]
    return value[:-1*padsize]

def padding_pkcs5(value):
    padsize = AES.block_size - len(value) % AES.block_size
    return value + bytes([padsize] * padsize)
 
def remove_padding_pkcs5(value):
    padsize = value[len(value) - 1]
    return value[:-1*padsize]


def encrypt(data, password):
    """AES encrypt with AES/ECB/Pkcs5padding/SHA1PRNG options
    """
    data_padded = padding_pkcs5(data)
    key = get_sha1prng_key(password)
    cipher = AES.new(key, AES.MODE_ECB)
    data_encrypted = cipher.encrypt(data_padded)
    return data_encrypted

def decrypt(data_encrypted, password):
    """AES decrypt with AES/ECB/Pkcs5padding/SHA1PRNG options
    """
    key = get_sha1prng_key(password)
    cipher = AES.new(key, AES.MODE_ECB)
    data_padded = cipher.decrypt(data_encrypted)
    data = remove_padding_pkcs5(data_padded)
    return data

def encrypt_and_base64encode(text, password):
    data = text.encode()
    data_encrypted = encrypt(data, password)
    data_base64_encoded = base64.encodebytes(data_encrypted).decode()
    return strutils.join_lines(data_base64_encoded)

def decrypt_and_base64decode(text, password):
    data_encrypted = base64.decodebytes(text.encode())
    data = decrypt(data_encrypted, password)
    return data.decode()

def encrypt_and_safeb64encode(text, password):
    data = text.encode()
    data_encrypted = encrypt(data, password)
    data_safeb64_encoded = base64.urlsafe_b64encode(data_encrypted).decode()
    return strutils.join_lines(data_safeb64_encoded)

def decrypt_and_safeb64decode(text, password):
    data_encrypted = base64.urlsafe_b64decode(text.encode())
    data = decrypt(data_encrypted, password)
    return data.decode()

def encrypt_and_hexlify(text, password):
    data = text.encode()
    data_encrypted = encrypt(data, password)
    data_hexlified = binascii.hexlify(data_encrypted).decode()
    return data_hexlified

def decrypt_and_unhexlify(text, password):
    data_encrypted = binascii.unhexlify(text.encode())
    data = decrypt(data_encrypted, password)
    return data.decode()
