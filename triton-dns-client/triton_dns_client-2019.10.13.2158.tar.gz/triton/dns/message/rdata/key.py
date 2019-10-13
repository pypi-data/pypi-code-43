import base64

import triton
from .base import ResourceRecord


class KEY(ResourceRecord):
    class _Binary(ResourceRecord._Binary):

        @property
        def full(self):
            result = bin(self.resource_record.flags)[2:].zfill(16)
            result += bin(self.resource_record.protocol)[2:].zfill(8)
            result += bin(self.resource_record.algorithm)[2:].zfill(8)
            row = self.resource_record.public_key.decode()
            res = ''.join([bin(i)[2:].zfill(8) for i in [ord(c) for c in row]])
            result += res
            return result

    id = 25
    repr = ['flags', 'protocol', 'algorithm', 'public_key']

    @classmethod
    def parse_bytes(cls, answer, read_len):
        instance = cls(answer)
        instance.flags = answer.message.stream.read(f'bin:16')
        instance._protocol = answer.message.stream.read(f'uint:8')
        instance._algorithm = answer.message.stream.read(f'uint:8')
        str_ = answer.message.stream.read(f'bin:{read_len - 4}')
        instance._public_key = ''.join([chr(int(x, base=2)) for x in [str[i:i + 8] for i in range(0, len(str_), 8)]])
        return instance

    @classmethod
    def parse_dict(cls, answer, data):
        instance = cls(answer)
        instance.flags = data.get('flags')
        instance._protocol = 3
        instance._algorithm = data.get('algorithm')
        instance._public_key = data.get('public_key')
        return instance

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
