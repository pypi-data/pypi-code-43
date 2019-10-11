from bitstring import BitArray

import triton
from .base import ResourceRecord


class DS(ResourceRecord):
    class _Binary(ResourceRecord._Binary):

        @property
        def full(self):
            result = bin(self.resource_record.key_tag)[2:].zfill(16)
            result += bin(self.resource_record._algorithm)[2:].zfill(8)
            result += bin(self.resource_record._digest_type)[2:].zfill(8)
            result += BitArray(bytes=self.resource_record._digest).bin
            return result

    id = 43
    repr = ['key_tag', 'algorithm', 'algorithm', 'digest_type', 'digest']

    @classmethod
    def parse_bytes(cls, answer, read_len):
        """
        Parses wire-format bytes to DS instance
        :param answer: triton.dns.message.Answer
        :param read_len: Answer.rdata_length
        :return: DS instance
        """
        instance = cls(answer)
        instance.key_tag = answer.message.stream.read(f'uint:16')
        instance._algorithm = answer.message.stream.read(f'uint:8')
        instance._digest_type = answer.message.stream.read(f'uint:8')
        instance._digest = answer.message.stream.read(f'bytes:{read_len - 4}')
        return instance

    @classmethod
    def parse_dict(cls, answer, data):
        """
        Parses dict values to create this RR type
        :param answer: triton.dns.message.Answer
        :param data: dictionary with {'key_tag', 'algorithm', 'digest_type', 'digest'} values
        :return: DS instance
        """
        instance = cls(answer)
        instance.key_tag = data.get('key_tag')
        instance._algorithm = data.get('algorithm')
        instance._digest_type = data.get('digest_type')
        instance._digest = data.get('digest')
        return instance

    @property
    def digest(self):
        """
        digest field is represented as HEX according to RFC
        :return: hex value of _digest
        """
        return self._digest.hex()

    @property
    def algorithm(self):
        return triton.dns.dnssec.algorithms.Algorithm.find_by_id(self._algorithm).__name__

    @property
    def digest_type(self):
        return triton.dns.dnssec.digest.Digest.by_id(self._digest_type).__name__

    @property
    def __dict__(self):
        """
        Monkey-patch dict. Excludes all unnecessary attr
        :return: dict of fields according to RFC
        """
        return {'flags': int(self.key_tag),
                'protocol': int(self._algorithm),
                'algorithm': int(self._digest_type),
                'public_key': str(self._digest)}

    def verify_key(self, key):
        """
        Verifies that DNSKEY answer matches this DS record digest
        :param key: triton.dns.message.Answer
        :return: True if matches, False if not. Raises if key_tag dont match
        """
        return triton.dns.dnssec.digest.Digest.verify_from_ds(key, self.answer)

    def verify_from_message(self, message):
        """
        Verifies that corresponding DNSKEY exist in message and its correct
        :param message: triton.dns.Message
        :return: True is exist and matches and False in any other condition
        """
        for answer in message.answer.by_type(triton.dns.message.rdata.DNSKEY):
            if answer.rdata.key_tag == self.key_tag:
                return triton.dns.dnssec.digest.Digest.verify_from_ds(answer, self.answer)
        return False

    @classmethod
    def from_json(cls, answer, data):
        instance = cls(answer)
        instance.key_tag = data.get('key_tag')
        instance._algorithm = triton.dns.dnssec.algorithms.Algorithm.find_by_name(data.get('algorithm')).id
        instance._digest_type = data.get('digest_type')
        instance._digest = bytes.fromhex(data.get('digest'))
        return instance
