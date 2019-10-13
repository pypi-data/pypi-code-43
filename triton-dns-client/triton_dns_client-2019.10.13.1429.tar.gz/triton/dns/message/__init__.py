import json
import random

from bitstring import ConstBitStream, BitArray

from .answer import Answer, AnswerStorage
from .domains.storage import DomainStorage
from .header import Header
from .question import Question, QuestionStorage
from .rdata import RRSIG, DS
from ..dnssec.exceptions import VerificationError
import asyncio

class Message:
    class _Binary:
        def __init__(self, message):
            self.message = message

        @property
        def full(self):
            self.message.offset = 0
            self.message.domains.storage.clear()
            result = self.message.header.Binary.full
            result += self.message.question.Binary.full
            result += self.message.answer.Binary.full
            result += self.message.authority.Binary.full
            result += self.message.additional.Binary.full
            return BitArray(bin=result).bytes

        @property
        def reply(self):
            self.message.offset = 0
            self.message.domains.storage.clear()
            result = self.message.answers.Binary.full
            result += self.message.authority.Binary.full
            result += self.message.additional.Binary.full
            return BitArray(bin=result).bytes

    def __init__(self):
        self.question = QuestionStorage(self)
        self.answer = AnswerStorage(self)
        self.authority = AnswerStorage(self)
        self.additional = AnswerStorage(self)
        self.domains = DomainStorage()
        self.offset = 0
        self.Binary = self._Binary(self)

    @classmethod
    def parse_bytes(cls, raw_bytes):
        message = cls()
        message.stream = ConstBitStream(raw_bytes)
        message.header = Header.parse_bytes(message)
        for _ in range(message.header._qdcount):
            message.question.append(Question.parse_bytes(message))
        for _ in range(message.header._ancount):
            message.answer.append(Answer.parse_bytes(message))
        for _ in range(message.header._nscount):
            message.authority.append(Answer.parse_bytes(message))
        for _ in range(message.header._arcount):
            message.additional.append(Answer.parse_bytes(message))
        message.domains.purge()
        return message

    def add_dict(self, data: dict) -> None:
        for answ in data.get('answer', []):
            self.add_dict_answer(answ)
        for auth in data.get('authority', []):
            self.add_dict_authority(auth)
        for addi in data.get('additional', []):
            self.add_dict_additional(addi)

    def add_dict_answer(self, data):
        self.answer.append(Answer.parse_dict(self, data))

    def add_dict_authority(self, data):
        self.authority.append(Answer.parse_dict(self, data))

    def add_dict_additional(self, data):
        self.additional.append(Answer.parse_dict(self, data))

    @classmethod
    def parse_dict(cls, data):
        message = cls()
        message.header = Header.parse_dict(message, data['header'])
        message.question = QuestionStorage.parse_dict(message, data['question'])
        message.answer = AnswerStorage.parse_dict(message, data['answer'])
        message.authority = AnswerStorage.parse_dict(message, data['authority'])
        message.additional = AnswerStorage.parse_dict(message, data['additional'])
        message.domains.purge()
        return message

    @property
    def __dict__(self):
        return {'header': self.header.__mydict__(),
                'question': [x.__mydict__() for x in self.question],
                'answer': [x.__mydict__() for x in self.answer],
                'authority': [x.__mydict__() for x in self.authority],
                'additional': [x.__mydict__() for x in self.additional]
                }

    def __repr__(self):
        return str({'header': self.header,
                    'question': self.question,
                    'answer': self.answer,
                    'authority': self.authority,
                    'additional': self.additional})

    def to_json(self):
        return json.dumps(json.loads(str(self.__repr__()).replace("'", '"')), indent=4)

    def from_json(self, data):
        data = json.loads(data)
        for answ in data.get('answer', []):
            self.from_json_answer(answ)
        for auth in data.get('authority', []):
            self.from_json_authority(auth)
        for addi in data.get('additional', []):
            self.from_json_additional(addi)

    def from_json_answer(self, data):
        self.answer.append(Answer.from_json(self, data))

    def from_json_additional(self, data):
        self.authority.append(Answer.from_json(self, data))

    def from_json_authority(self, data):
        self.additional.append(Answer.from_json(self, data))

    @classmethod
    def create_question(cls, name, qtype=1, qclass=1, dnssec=False):
        m = Message.parse_dict(
            {
                'header': {
                    'id': random.randrange(1, 65535),
                    'qr': 0,
                    'opcode': 0,
                    'aa': 0,
                    'tc': 0,
                    'rd': 1,
                    'ra': 0,
                    'z': 0,
                    'rcode': 0,
                    'qdcount': 1,
                    'ancount': 0,
                    'nscount': 0,
                    'arcount': 0
                },
                'question': [
                    {
                        'qname': name,
                        'qtype': qtype,
                        'qclass': qclass
                    }
                ],
                'answer': [],
                'authority': [],
                'additional': [] if not dnssec else [
                    {
                        'name': '',
                        'type': 41,
                        'class': 4096,
                        'ttl': int('00000000000000001000000000000000', base=2),
                        'rdata': {
                            'options': []
                        }
                    }
                ]
            }
        )
        return m

    @classmethod
    def sync_create_question(cls, *args, **kwargs):
        return asyncio.run(cls.create_question(*args, **kwargs))


    @property
    def reply_data(self):
        return [self.answer, self.authority, self.additional]

    async def verify_rrsig(self, keys):
        results = []
        for sig in self.answer.by_type(RRSIG):
            results.append(sig.rdata.verify(keys, self.answer))
        for sig in self.authority.by_type(RRSIG):
            results.append(sig.rdata.verify(keys, self.authority))
        for sig in self.additional.by_type(RRSIG):
            results.append(sig.rdata.verify(keys, self.additional))
        if not all(results):
            raise VerificationError()
        return True

    async def verify_keys(self, ds_message):
        ds = ds_message.answer.by_type(DS)
        assert len(ds) == 1
        ds = ds[0]
        return ds.rdata.verify_from_message(self)
