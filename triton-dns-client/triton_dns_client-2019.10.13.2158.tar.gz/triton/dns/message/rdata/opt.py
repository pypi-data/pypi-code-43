from .base import ResourceRecord


class OPT(ResourceRecord):
    class _Binary(ResourceRecord._Binary):

        @property
        def full(self):
            return self.resource_record.storage.Binary.full

    id = 41
    repr = ['storage']

    def __init__(self, *args, **kwargs):
        super(OPT, self).__init__(*args, **kwargs)
        self.storage = OptionStorage()

    @classmethod
    def parse_bytes(cls, answer, read_len):
        instance = cls(answer)

        while read_len > 0:
            option_code = answer.message.stream.read(f'uint:2')
            option_length = answer.message.stream.read(f'uint:2')
            option_data = answer.message.stream.read(f'bin:{8 * option_length}')
            instance.storage.append(Option(option_code, option_data))
            read_len -= 2 + 2 + option_length
        return instance

    @classmethod
    def parse_dict(cls, answer, data):
        instance = cls(answer)
        for opt in data.get('options', []):
            instance.storage.append(Option(**opt))
        return instance

    @property
    def __dict__(self):
        return {'storage': self.storage.__dict__}

    @classmethod
    def from_json(cls, answer, data):
        instance = cls(answer)
        for opt in data.get('options', []):
            instance.storage.append(Option(**opt))
        return instance


class Option:
    class _Binary:
        def __init__(self, opt):
            self.opt = opt

        @property
        def full(self):
            result = bin(self.opt.code)[2:].zfill(16)
            result += bin(self.opt.length)[2:].zfill(16)
            result += bin(self.opt.data)[2:].zfill(self.opt.length)
            return result

    def __init__(self, code, data):
        self.code = code
        self.data = data

    @property
    def length(self):
        return int(len(self.data) / 8)


class OptionStorage:
    class _Binary:
        def __init__(self, storage):
            self.storage = storage

        @property
        def full(self):
            result = ''
            for x in self.storage.storage:
                result += x.Binary.full
            return result

    def __init__(self):
        self.storage = []
        self.Binary = self._Binary(self)

    def append(self, option):
        self.storage.append(option)

    def __repr__(self):
        return str({x.code: x.data for x in self.storage})

    @property
    def __dict__(self):
        return {x.code: x.data for x in self.storage}
