from triton.dns.message.domains.domain import Domain
from .base import ResourceRecord


class CNAME(ResourceRecord):
    class _Binary(ResourceRecord._Binary):

        @property
        def full(self):
            return self.resource_record.cname.sub_encode(self.resource_record.cname.label)

    id = 5
    repr = ['cname']

    @classmethod
    def parse_bytes(cls, answer, read_len):
        instance = cls(answer)
        instance.cname = Domain.decode(answer.message)
        return instance

    @classmethod
    def parse_dict(cls, answer, data):
        instance = cls(answer)
        instance.cname = Domain(data.get('cname'), None)
        return instance

    @property
    def __dict__(self):
        return {'cname': self.cname.label}

    @classmethod
    def from_json(cls, answer, data):
        instance = cls(answer)
        instance.address = Domain(data.get('address'), None)
        return instance
