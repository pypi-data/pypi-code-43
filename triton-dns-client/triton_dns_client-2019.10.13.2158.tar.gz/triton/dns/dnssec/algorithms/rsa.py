from Cryptodome.Hash import SHA1, SHA256, SHA512, SHA
from Cryptodome.PublicKey import RSA
from Cryptodome.Signature import PKCS1_v1_5

from .base import Algorithm


class RSAPublicKey:
    def __init__(self, rr):
        len_pe = rr.rdata._public_key[0]
        self.public_exponent = int.from_bytes(rr.rdata._public_key[1:1 + len_pe], byteorder='big')
        self.modulus = int.from_bytes(rr.rdata._public_key[1 + len_pe:], byteorder='big')


class RSAAlgorithm(Algorithm):
    signer = RSA
    hasher: SHA

    @classmethod
    def construct_signer(cls, key_rr):
        rsa_key = RSAPublicKey(key_rr)
        _key = cls.signer.construct((rsa_key.modulus, rsa_key.public_exponent))
        return PKCS1_v1_5.new(_key)


class RSASHA1(RSAAlgorithm):
    id = 5
    signer = RSA
    hasher = SHA1


class RSASHA1_NSEC3_SHA1(RSAAlgorithm):
    id = 7
    signer = RSA
    hasher = SHA1


class RSASHA256(RSAAlgorithm):
    id = 8
    signer = RSA
    hasher = SHA256


class RSASHA512(RSAAlgorithm):
    id = 10
    signer = RSA
    hasher = SHA512
