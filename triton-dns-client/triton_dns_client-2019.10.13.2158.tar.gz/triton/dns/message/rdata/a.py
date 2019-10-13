from ipaddress import IPv4Address

from .base import ResourceRecord


class A(ResourceRecord):
    class _Binary(ResourceRecord._Binary):

        @property
        def full(self):
            return bin(int(self.resource_record.address))[2:].zfill(8 * 4)

    id = 1
    repr = ['address']

    @classmethod
    def parse_bytes(cls, answer, read_len):
        instance = cls(answer)
        instance.address = IPv4Address(answer.message.stream.read(f'uint:{read_len * 8}'))
        return instance

    @classmethod
    def parse_dict(cls, answer, data):
        instance = cls(answer)
        instance.address = IPv4Address(data.get('address'))
        return instance

    @property
    def __dict__(self):
        return {'address': int(self.address)}

    @classmethod
    def from_json(cls, answer, data):
        instance = cls(answer)
        instance.address = IPv4Address(data.get('address'))
        return instance
