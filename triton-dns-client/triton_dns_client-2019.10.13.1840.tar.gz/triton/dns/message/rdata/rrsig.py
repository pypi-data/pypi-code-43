import base64
import datetime

from bitstring import BitArray, BitStream

from triton.dns.dnssec.algorithms import Algorithm
from triton.dns.message.domains.domain import Domain
from .base import ResourceRecord
from .dnskey import DNSKEY


class RRSIG(ResourceRecord):
    type_covered: int
    algorithm: int
    labels: int
    original_ttl: int
    signature_expiration: int
    signature_inception: int
    key_tag: int
    signers_name: str
    signature: bytes

    class _Binary(ResourceRecord._Binary):

        @property
        def full(self):
            result = format(self.resource_record._type_covered, 'b').zfill(16)
            result += format(self.resource_record.algorithm, 'b').zfill(8)
            result += format(self.resource_record.labels, 'b').zfill(8)
            result += format(self.resource_record.original_ttl, 'b').zfill(32)
            result += format(self.resource_record.signature_expiration, 'b').zfill(32)
            result += format(self.resource_record.signature_inception, 'b').zfill(32)
            result += format(self.resource_record.key_tag, 'b').zfill(16)
            result += self.resource_record.signers_name.sub_encode(self.resource_record.signers_name.label)
            result += BitArray(bytes=self.resource_record._signature).bin
            return result

        @property
        def without_signature(self):
            result = format(self.resource_record._type_covered, 'b').zfill(16)
            result += format(self.resource_record._algorithm, 'b').zfill(8)
            result += format(self.resource_record.labels, 'b').zfill(8)
            result += format(self.resource_record.original_ttl, 'b').zfill(32)
            result += format(self.resource_record._signature_expiration, 'b').zfill(32)
            result += format(self.resource_record._signature_inception, 'b').zfill(32)
            result += format(self.resource_record.key_tag, 'b').zfill(16)
            result += self.resource_record.signers_name.sub_encode(self.resource_record.signers_name.label.lower())
            return result

    id = 46
    repr = ['type_covered',
            'algorithm',
            'labels',
            'original_ttl',
            'signature_expiration',
            'signature_inception',
            'key_tag',
            'signers_name',
            'signature']

    @classmethod
    def parse_bytes(cls, answer, read_len):
        instance = cls(answer)
        start = answer.message.stream.pos
        instance._type_covered = answer.message.stream.read(f'uint:16')
        instance._algorithm = answer.message.stream.read(f'uint:8')
        instance.labels = answer.message.stream.read(f'uint:8')
        instance.original_ttl = answer.message.stream.read(f'uint:32')
        instance._signature_expiration = answer.message.stream.read(f'uint:32')
        instance._signature_inception = answer.message.stream.read(f'uint:32')
        instance.key_tag = answer.message.stream.read(f'uint:16')
        instance.signers_name = Domain.decode(answer.message)
        end = answer.message.stream.pos
        instance._signature = answer.message.stream.read(f'bytes:{int(read_len - (end - start) / 8)}')
        return instance

    @classmethod
    def parse_raw(cls, data):
        instance = cls(None)
        stream = BitStream(bytes=data)
        instance._type_covered = stream.read(f'uint:16')
        instance._algorithm = stream.read(f'uint:8')
        instance.labels = stream.read(f'uint:8')
        instance.original_ttl = stream.read(f'uint:32')
        instance._signature_expiration = stream.read(f'uint:32')
        instance._signature_inception = stream.read(f'uint:32')
        instance.key_tag = stream.read(f'uint:16')
        instance.signers_name = Domain.decode(None)
        end = stream.pos
        instance._signature = stream.read(f'bytes:{int(len(data) - end / 8)}')
        return instance

    @property
    def signature(self):
        return base64.b64encode(self._signature).decode()

    @classmethod
    def parse_dict(cls, answer, data):
        instance = cls(answer)
        instance._type_covered = data.get('type_covered')
        instance._algorithm = data.get('algorithm')
        instance.labels = data.get('labels')
        instance.original_ttl = data.get('original_ttl')
        instance._signature_expiration = data.get('signature_expiration')
        instance._signature_inception = data.get('signature_inception')
        instance.key_tag = data.get('key_tag')
        instance.signers_name = Domain(data.get('signers_name'))
        instance._signature = data.get('signature')
        return instance

    @property
    def algorithm(self):
        return Algorithm.find_by_id(self._algorithm).__name__

    @property
    def type_covered(self):
        return ResourceRecord.find_subclass_by_id(self._type_covered).__name__

    @property
    def signature_expiration(self):
        return datetime.datetime.fromtimestamp(self._signature_expiration, tz=datetime.timezone.utc)

    @property
    def signature_inception(self):
        return datetime.datetime.fromtimestamp(self._signature_inception, tz=datetime.timezone.utc)

    @property
    def __dict__(self):
        return {'type_covered': int(self._type_covered),
                'algorithm': int(self._algorithm),
                'labels': int(self.labels),
                'original_ttl': int(self.original_ttl),
                'signature_expiration': int(self._signature_expiration),
                'signature_inception': int(self._signature_inception),
                'key_tag': int(self.key_tag),
                'signers_name': str(self.signers_name.label),
                'signature': str(self._signature)}

    def verify(self, keys, search_in):
        covered_type = ResourceRecord.find_subclass_by_id(self._type_covered)
        assert covered_type in search_in
        for key in keys.answer.by_type(DNSKEY):
            if key.rdata.key_tag == self.key_tag:
                algo = Algorithm.find_by_id(self._algorithm)
                return algo.verify_rrset(key, search_in.by_type(covered_type), self.answer)
        else:
            raise Exception('No matching key')

    @classmethod
    def from_json(cls, answer, data):
        instance = cls(answer)
        instance._type_covered = ResourceRecord.fin_subclass_by_name(data.get('type_covered')).id
        instance._algorithm = Algorithm.find_by_name(data.get('algorithm')).id
        instance.labels = data.get('labels')
        instance.original_ttl = data.get('original_ttl')
        instance._signature_expiration = datetime.datetime.fromisoformat(data.get('signature_expiration'))
        instance._signature_inception = datetime.datetime.fromisoformat(data.get('signature_inception'))
        instance.key_tag = data.get('key_tag')
        instance.signers_name = Domain(data.get('signers_name'), None)
        instance._signature = base64.b64decode(data.get('signature'))
        return instance
