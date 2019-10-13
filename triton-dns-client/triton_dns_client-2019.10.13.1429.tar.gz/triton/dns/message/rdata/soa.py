from .base import ResourceRecord
from ..domains.domain import Domain


class SOA(ResourceRecord):
    class _Binary(ResourceRecord._Binary):

        @property
        def full(self):
            result = Domain.sub_encode(self.resource_record.mname.label)
            result += Domain.sub_encode(self.resource_record.rname.label)
            result += bin(int(self.resource_record.serial))[2:].zfill(32)
            result += bin(int(self.resource_record.refresh))[2:].zfill(32)
            result += bin(self.resource_record.retry)[2:].zfill(32)
            result += bin(self.resource_record.expire)[2:].zfill(32)
            result += bin(self.resource_record.minimum)[2:].zfill(32)
            return result

    id = 6
    repr = ['mname', 'rname', 'serial', 'refresh', 'retry', 'expire', 'minimum']

    @classmethod
    def parse_bytes(cls, answer, read_len):
        instance = cls(answer)
        instance.mname = Domain.decode(answer.message)
        instance.rname = Domain.decode(answer.message)
        instance.serial = answer.message.stream.read('uint:32')
        instance.refresh = answer.message.stream.read('uint:32')
        instance.retry = answer.message.stream.read('uint:32')
        instance.expire = answer.message.stream.read('uint:32')
        instance.minimum = answer.message.stream.read('uint:32')
        return instance

    @classmethod
    def parse_dict(cls, answer, data):
        instance = cls(answer)
        instance.mname = Domain(data.get('mname'), None)
        instance.rname = Domain(data.get('rname'), None)
        instance.serial = data.get('serial')
        instance.refresh = data.get('refresh')
        instance.retry = data.get('retry')
        instance.expire = data.get('expire')
        instance.minimum = data.get('minimum')
        return instance

    @property
    def __dict__(self):
        return {'mname': self.mname.label,
                'rname': self.rname.label,
                'serial': self.serial,
                'refresh': self.refresh,
                'retry': self.retry,
                'expire': self.expire,
                'minimum': self.minimum}

    @classmethod
    def from_json(cls, answer, data):
        instance = cls(answer)
        instance.mname = Domain(data.get('mname'), None)
        instance.rname = Domain(data.get('rname'), None)
        instance.serial = data.get('serial')
        instance.refresh = data.get('refresh')
        instance.retry = data.get('retry')
        instance.expire = data.get('expire')
        instance.minimum = data.get('minimum')
        return instance
