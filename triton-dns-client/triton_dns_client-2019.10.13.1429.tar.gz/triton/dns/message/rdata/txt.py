from .base import ResourceRecord


class TXT(ResourceRecord):
    class _Binary(ResourceRecord._Binary):

        @property
        def full(self):
            res = ''.join([bin(i)[2:].zfill(8) for i in [ord(c) for c in self.resource_record.txt_data]])
            return f'{bin(int(len(res) / 8))[2:].zfill(8)}{res}'

    id = 16
    repr = ['txt_data']

    @classmethod
    def parse_bytes(cls, answer, read_len):
        instance = cls(answer)
        str = answer.message.stream.read(f'bin:{read_len * 8}')
        instance.txt_data = ''.join([chr(int(x, base=2)) for x in [str[i:i + 8] for i in range(0, len(str), 8)]][1:])
        return instance

    @classmethod
    def parse_dict(cls, answer, data):
        instance = cls(answer)
        instance.txt_data = data.get('txt_data')
        return instance

    @property
    def __dict__(self):
        return {'txt_data': self.txt_data}

    @classmethod
    def from_json(cls, answer, data):
        instance = cls(answer)
        instance.txt_data = data.get('txt_data')
        return instance
