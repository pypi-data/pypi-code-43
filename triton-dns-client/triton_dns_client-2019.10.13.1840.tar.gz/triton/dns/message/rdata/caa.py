from .base import ResourceRecord


class CAA(ResourceRecord):
    class _Binary(ResourceRecord._Binary):

        @property
        def full(self):
            result = format(self.resource_record.critical, 'b').zfill(8)
            result += format(len(self.resource_record.tag), 'b').zfill(8)
            result += ''.join([bin(i)[2:].zfill(8) for i in [ord(c) for c in self.resource_record.tag]])
            result += ''.join([bin(i)[2:].zfill(8) for i in [ord(c) for c in self.resource_record.value]])
            return result

    id = 257
    repr = ['critical', 'tag', 'value']

    @classmethod
    def parse_bytes(cls, answer, read_len):
        # TODO: bytes parser
        instance = cls(answer)
        instance.critical = bool(answer.message.stream.read(f'uint:8'))
        instance.tag_length = answer.message.stream.read(f'uint:8')
        str_tag = answer.message.stream.read(f'bin:{instance.tag_length * 8}')
        instance.tag = ''.join([chr(int(x, base=2)) for x in [str_tag[i:i + 8] for i in range(0, len(str_tag), 8)]])
        str_value = answer.message.stream.read(f'bin:{(read_len - instance.tag_length - 2) * 8}')
        instance.value = ''.join(
            [chr(int(x, base=2)) for x in [str_value[i:i + 8] for i in range(0, len(str_value), 8)]])
        return instance

    @classmethod
    def parse_dict(cls, answer, data):
        instance = cls(answer)
        instance.critical = data.get('critical')
        instance.tag = data.get('tag')
        instance.value = data.get('value')
        return instance

    @property
    def __dict__(self):
        return {'critical': int(self.critical),
                'tag': str(self.tag),
                'value': str(self.value)}

    @classmethod
    def from_json(cls, answer, data):
        instance = cls(answer)
        instance.critical = data.get('critical')
        instance.tag = data.get('tag')
        instance.value = data.get('value')
        return instance
