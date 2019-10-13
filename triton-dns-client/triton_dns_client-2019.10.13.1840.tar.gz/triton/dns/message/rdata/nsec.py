import base64

from bitstring import BitArray

from triton.dns.dnssec.digest import Digest
from triton.dns.message.domains.domain import Domain
from .base import ResourceRecord


class BitMapWindow:
    def __init__(self, number, length, data):
        self.number = number
        self.length = length
        self.data = data

    def __len__(self):
        return 2 + self.length

    @property
    def __dict__(self):
        return {'number': self.number,
                'length': self.length,
                'data': self.data}

    @property
    def binary(self):
        return bin(self.number)[2:].zfill(8) + bin(self.length)[2:].zfill(8) + self.data.zfill(8 * self.length)


class BitMapWindowStorage:
    def __init__(self):
        self.storage = []

    def push(self, window):
        assert isinstance(window, BitMapWindow)
        self.storage.append(window)

    def __len__(self):
        return sum([len(bmw) for bmw in self.storage])

    @property
    def types(self):
        types_ = []
        for window in self.storage:
            if window.number == 0:
                for n, b in enumerate(window.data):
                    if n == 0:
                        continue
                    if b == '1':
                        try:
                            types_.append(ResourceRecord.find_subclass_by_id(n))
                        except ValueError:
                            pass
            if window.number == 1:
                if window.data[1] == '1':
                    types_.append(ResourceRecord.find_subclass_by_id(257))
                if window.data[2] == '1':
                    types_.append(ResourceRecord.find_subclass_by_id(258))
        return types_

    def __repr__(self):
        return ', '.join([x.__name__ for x in self.types])

    @classmethod
    def from_list(cls, data):
        instance = cls()
        for item in data:
            instance.push(BitMapWindow(**item))
        return instance

    @property
    def __dict__(self):
        return [bmw.__dict__ for bmw in self.storage]

    @property
    def binary(self):
        return ''.join([x.binary for x in self.storage])

    @classmethod
    def from_json(cls, data):
        instance = cls()
        for item in data:
            instance.push(BitMapWindow(**item))
        return instance


class NSEC(ResourceRecord):
    class _Binary(ResourceRecord._Binary):

        @property
        def full(self):
            result = self.resource_record.next_domain_name.sub_encode(self.resource_record.next_domain_name.label)
            result += BitArray(bytes=self.resource_record.type_bitmaps).bin
            return result

    id = 47
    repr = ['next_domain_name',
            'type_bitmaps_']

    @classmethod
    def parse_bytes(cls, answer, read_len):
        instance = cls(answer)
        instance.next_domain_name = Domain.decode(answer.message)
        instance.type_bitmaps_ = BitMapWindowStorage()
        wn = answer.message.stream.read('uint:8')
        wlen = answer.message.stream.read('uint:8')
        instance.type_bitmaps_.push(BitMapWindow(wn, wlen, answer.message.stream.read(f'bin:{8 * wlen}')))
        if answer.message.stream.peek('uint:8') == 1:
            wn = answer.message.stream.read('uint:8')
            wlen = answer.message.stream.read('uint:8')
            instance.type_bitmaps_.push(BitMapWindow(wn, wlen, answer.message.stream.read(f'bin:{8 * wlen}')))
        return instance

    @classmethod
    def parse_dict(cls, answer, data):
        instance = cls(answer)
        instance.next_domain_name = Domain(data.get('next_domain_name'))
        instance.type_bitmaps_ = BitMapWindowStorage.from_list(data.get('type_bitmaps'))
        return instance

    @property
    def type_bitmaps(self):
        return self.type_bitmaps_.__dict__

    def __dict__(self):
        return {'next_domain_name': self.next_domain.name.label,
                'type_bitmaps_': self.type_bitmaps}

    @classmethod
    def from_json(cls, answer, data):
        instance = cls(answer)
        instance.next_domain_name = Domain(data.get('next_domain_name'), None)
        instance.type_bitmaps_ = BitMapWindowStorage.from_list(data.get('type_bitmaps'))
        return instance


class NSEC3(ResourceRecord):
    class _Binary(ResourceRecord._Binary):

        @property
        def full(self):
            result = bin(self.resource_record._hash_algorithm)[2:].zfill(8)
            result += bin(self.resource_record.flags)[2:].zfill(8)
            result += bin(self.resource_record.iterations)[2:].zfill(16)
            result += bin(self.resource_record.salt_length)[2:].zfill(8)
            result += BitArray(bytes=self.resource_record._salt).bin
            result += bin(self.resource_record.hash_length)[2:].zfill(8)
            result += BitArray(bytes=self.resource_record._next_hashed_owner_name).bin
            result += self.resource_record.type_bitmaps_.binary
            return result

    id = 50

    repr = ['hash_algorithm',
            'flags',
            'iterations',
            'salt',
            'next_hashed_owner_name',
            'type_bitmaps_']

    @classmethod
    def parse_bytes(cls, answer, read_len):
        instance = cls(answer)
        instance._hash_algorithm = answer.message.stream.read('uint:8')
        instance.flags = answer.message.stream.read('uint:8')
        instance.iterations = answer.message.stream.read('uint:16')
        instance.salt_length = answer.message.stream.read('uint:8')
        instance._salt = answer.message.stream.read(f'bytes:{instance.salt_length}')
        instance.hash_length = answer.message.stream.read('uint:8')
        instance._next_hashed_owner_name = answer.message.stream.read(f'bytes:{instance.hash_length}')
        instance.type_bitmaps_ = BitMapWindowStorage()
        wn = answer.message.stream.read('uint:8')
        wlen = answer.message.stream.read('uint:8')
        instance.type_bitmaps_.push(BitMapWindow(wn, wlen, answer.message.stream.read(f'bin:{8 * wlen}')))
        if answer.message.stream.peek('uint:8') == 1:
            wn = answer.message.stream.read('uint:8')
            wlen = answer.message.stream.read('uint:8')
            instance.type_bitmaps_.push(BitMapWindow(wn, wlen, answer.message.stream.read(f'bin:{8 * wlen}')))
        return instance

    @classmethod
    def parse_dict(cls, answer, data: dict):
        instance = cls(answer)
        instance._hash_algorithm = data.get('hash_algorithm')
        instance.flags = data.get('flags')
        instance.iterations = data.get('iterations')
        instance.salt_length = len(data.get('salt'))
        instance._salt = data.get('salt')
        instance.hash_length = len(data.get('next_hashed_owner_name'))
        instance._next_hashed_owner_name = data.get('next_hashed_owner_name')
        instance.bitmap_windows = BitMapWindowStorage.from_list(data.get('type_bitmaps'))
        return instance

    @property
    def hash_algorithm(self):
        return Digest.by_id(self._hash_algorithm).__name__

    @property
    def salt(self):
        return self._salt.hex().upper()

    @property
    def next_hashed_owner_name(self):
        result = self._next_hashed_owner_name
        missing_padding = len(self._next_hashed_owner_name) % 2
        if missing_padding:
            result += b'=' * (2 - missing_padding)
        return self._next_hashed_owner_name.hex()
        return base64.b64decode(result)  # TODO base32, not hex

    @property
    def __dict__(self):
        return {'hash_algorithm': self._hash_algorithm,
                'flags': self.flags,
                'salt_length': len(self._salt),
                'salt': self._salt,
                'hash_length': len(self.bitmap_windows),
                'type_bitmaps': self.bitmap_windows.__dict__}

    @classmethod
    def from_json(cls, answer, data):
        instance = cls(answer)
        instance._hash_algorithm = data.get('hash_algorithm')
        instance.flags = data.get('flags')
        instance.iterations = data.get('iterations')
        instance.salt_length = len(data.get('salt'))
        instance._salt = data.get('salt')
        instance.hash_length = len(data.get('next_hashed_owner_name'))
        instance._next_hashed_owner_name = data.get('next_hashed_owner_name')
        instance.bitmap_windows = BitMapWindowStorage.from_list(data.get('type_bitmaps'))
        return instance


class NSEC3PARAM(ResourceRecord):
    class _Binary(ResourceRecord._Binary):

        @property
        def full(self):
            result = bin(self.resource_record.hash_algorithm)[2:].zfill(8)
            result += bin(self.resource_record.flags)[2:].zfill(8)
            result += bin(self.resource_record.iterations)[2:].zfill(16)
            result += bin(self.resource_record.salt_length)[2:].zfill(8)
            result += BitArray(bytes=self.resource_record.salt).bin
            return result

    id = 51
    repr = ['hash_algorithm',
            'flags',
            'iterations',
            'salt']

    @classmethod
    def parse_bytes(cls, answer, read_len):
        instance = cls(answer)
        instance._hash_algorithm = answer.message.stream.read('uint:8')
        instance.flags = answer.message.stream.read('uint:8')
        instance.iterations = answer.message.stream.read('uint:16')
        instance.salt_length = answer.message.stream.read('uint:8')
        instance._salt = answer.message.stream.read(f'bytes:{instance.salt_length}')
        return instance

    @classmethod
    def parse_dict(cls, answer, data):
        instance = cls(answer)
        instance._hash_algorithm = data.get('hash_algorithm')
        instance.flags = data.get('flags')
        instance.iterations = data.get('iterations')
        instance.salt_length = data.get('salt_length')
        instance._salt = data.get('salt')
        return instance

    @property
    def hash_algorithm(self):
        return Digest.by_id(self._hash_algorithm).__name__

    @property
    def salt(self):
        return self._salt.hex().upper()

    @property
    def __dict__(self):
        return {'hash_algorithm': self._hash_algorithm,
                'flags': self.flags,
                'iterations': self.iterations,
                'salt_length': len(self.salt),
                'salt': self._salt}
