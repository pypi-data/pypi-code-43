from .base import ResourceRecord
from ..domains.domain import Domain


class PTR(ResourceRecord):
    class _Binary(ResourceRecord._Binary):

        @property
        def full(self):
            return self.resource_record.ptrdname.binary_raw

    id = 12

    repr = ['ptrdname']

    @classmethod
    def parse_bytes(cls, answer, read_len):
        instance = cls(answer)
        instance.ptrdname = Domain.decode(answer.message)
        return instance

    @classmethod
    def parse_dict(cls, answer, data):
        instance = cls(answer)
        instance.ptrdname = Domain(data.get('ptrdname'))
        return instance

    @property
    def __dict__(self):
        return {'ptrdname': self.ptrdname}

    @classmethod
    def from_json(cls, answer, data):
        instance = cls(answer)
        instance.ptrdname = Domain(data.get('ptrdname'))
        return instance