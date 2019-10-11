from .base import ResourceRecord
from ..domains.domain import Domain


class MX(ResourceRecord):
    class _Binary(ResourceRecord._Binary):

        @property
        def full(self):
            result = bin(int(self.resource_record.preference))[2:].zfill(16)
            result += Domain.sub_encode(self.resource_record.exchange.label)
            return result

    id = 15
    repr = ['preference', 'exchange']

    @classmethod
    def parse_bytes(cls, answer, read_len):
        instance = cls(answer)
        instance.preference = answer.message.stream.read(f'uint:{2 * 8}')
        instance.exchange = Domain.decode(answer.message)
        return instance

    @classmethod
    def parse_dict(cls, answer, data):
        instance = cls(answer)
        instance.preference = data.get('preference')
        instance.exchange = Domain(data.get('exchange'), None)
        return instance

    @property
    def __dict__(self):
        return {'preference': self.preference,
                'exchange': self.exchange.label}

    @classmethod
    def from_json(cls, answer, data):
        instance = cls(answer)
        instance.preference = data.get('preference')
        instance.exchange = Domain(data.get('exchange'), None)
        return instance
