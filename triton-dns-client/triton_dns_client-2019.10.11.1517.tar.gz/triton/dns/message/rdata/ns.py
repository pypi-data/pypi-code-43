from .base import ResourceRecord
from ..domains.domain import Domain


class NS(ResourceRecord):
    class _Binary(ResourceRecord._Binary):

        @property
        def full(self):
            return Domain.sub_encode(self.resource_record.nsdname.label)

    id = 2
    repr = ['nsdname']

    @classmethod
    def parse_bytes(cls, answer, read_len):
        instance = cls(answer)
        instance.nsdname = Domain.decode(answer.message)
        return instance

    @classmethod
    def parse_dict(cls, answer, data):
        instance = cls(answer)
        instance.nsdname = Domain(data.get('label', data.get('nsdname')), None)
        return instance

    @property
    def __dict__(self):
        return {'nsdname': self.nsdname.label}

    @classmethod
    def from_json(cls, answer, data):
        instance = cls(answer)
        instance.nsdname = Domain(data.get('label', data.get('nsdname')), None)
        return instance
