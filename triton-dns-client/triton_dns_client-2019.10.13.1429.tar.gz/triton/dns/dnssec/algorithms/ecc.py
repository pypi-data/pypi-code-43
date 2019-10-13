from Cryptodome.Hash import SHA256

from .base import Algorithm


class ECCAlgorithm(Algorithm):

    def construct_signer(cls, key_rr):
        print('found')
        print(key_rr.rdata._public_key)
        # key = ECC.construct(key_rr.rdata.public_key)


class ECDSAP256SHA256(ECCAlgorithm):
    hasher = SHA256
    id = 13


class ECDSAP384SHA384(ECCAlgorithm):
    id = 14


class ECCGOST(ECCAlgorithm):
    id = 12
