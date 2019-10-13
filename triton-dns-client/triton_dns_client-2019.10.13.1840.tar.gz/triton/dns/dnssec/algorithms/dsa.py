from Cryptodome.Hash import SHA1, SHA
from Cryptodome.PublicKey import DSA as Crypto_DSA

from .base import Algorithm


class DSAPublicKey:
    pass


class DSAAlgorithm(Algorithm):
    signer = Crypto_DSA
    hasher: SHA

    def construct_signer(cls, key_rr):
        pass


class DSA(DSAAlgorithm):
    hasher = None

    id = 3


class DSA_NSEC3_SHA1(DSAAlgorithm):
    hasher = SHA1

    id = 6
