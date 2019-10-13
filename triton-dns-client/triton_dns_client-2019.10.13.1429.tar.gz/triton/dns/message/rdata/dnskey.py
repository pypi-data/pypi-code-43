import base64

from bitstring import BitArray

import triton
from .base import ResourceRecord


class DNSKEY(ResourceRecord):
    class _Binary(ResourceRecord._Binary):

        @property
        def full(self):
            result = bin(self.resource_record.flags)[2:].zfill(16)
            result += bin(self.resource_record._protocol)[2:].zfill(8)
            result += bin(self.resource_record._algorithm)[2:].zfill(8)
            result += BitArray(bytes=self.resource_record._public_key).bin
            return result

    class KSK:
        pass

    class ZSK:
        pass

    id = 48
    repr = ['key_type', 'protocol', 'algorithm', 'public_key']

    @classmethod
    def parse_bytes(cls, answer: 'triton.dns.message.answer.Answer', read_len: int) -> 'DNSKEY':
        assert isinstance(answer, triton.dns.message.answer.Answer)
        assert isinstance(read_len, int)
        instance = cls(answer)
        instance.flags = answer.message.stream.read(f'uint:16')
        instance._protocol = answer.message.stream.read(f'uint:8')
        instance._algorithm = answer.message.stream.read(f'uint:8')
        instance._public_key = answer.message.stream.read(f'bytes:{read_len - 4}')
        assert isinstance(instance._public_key, bytes)
        return instance

    @classmethod
    def parse_dict(cls, answer: 'triton.dns.message.answer.Answer', data: dict) -> 'DNSKEY':
        assert isinstance(answer, triton.dns.message.answer.Answer)
        assert isinstance(data, dict)
        instance = cls(answer)
        instance.flags = data.get('flags')
        instance._protocol = 3
        instance._algorithm = data.get('algorithm')
        instance._public_key = data.get('public_key')
        assert isinstance(instance._public_key, bytes)
        return instance

    @property
    def public_key(self):
        return base64.b64encode(self._public_key).decode()

    @property
    def key_tag(self):
        if self._algorithm == 1:
            return 0
        else:
            ac = 0
            for i, k in enumerate(BitArray(bin=self.Binary.full).bytes):
                ac += k if i & 1 else k << 8
            ac += (ac >> 16) & 0xFFFF
            return ac & 0xFFFF

    @property
    def key_type(self):
        if self.flags == 257:
            return 'KSK'
        if self.flags == 256:
            return 'ZSK'

    @property
    def protocol(self):
        return self._protocol

    @property
    def algorithm(self):
        return triton.dns.dnssec.algorithms.Algorithm.find_by_id(self._algorithm).__name__

    @property
    def __dict__(self):
        return {'flags': self.flags,
                'protocol': self._protocol,
                'algorithm': self._algorithm,
                'public_key': self._public_key}

    @classmethod
    def from_json(cls, answer, data):
        instance = cls(answer)
        instance.flags = data.get('flags')
        instance._protocol = 3
        instance._algorithm = triton.dns.dnssec.algorithms.Algorithm.find_by_name(data.get('algorithm')).id
        instance._public_key = base64.b64decode(data.get('public_key'))
        return instance
