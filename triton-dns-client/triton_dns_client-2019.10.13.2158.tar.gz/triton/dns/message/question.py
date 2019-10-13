from .domains.domain import Domain


class Question:
    class _Binary:
        def __init__(self, question):
            self.question = question

        @property
        def full(self):
            result = self.question.qname.encode(self.question.message)
            result += bin(self.question.qtype)[2:].zfill(16)
            result += bin(self.question.qclass)[2:].zfill(16)
            self.question.message.offset += int(len(result) / 8)
            return result

    def __init__(self, message):
        self.message = message
        self.Binary = self._Binary(self)

    @classmethod
    def parse_bytes(cls, message):
        question = cls(message)
        question.qname = Domain.decode(message)
        question.qtype = message.stream.read('uint:16')
        question.qclass = message.stream.read('uint:16')
        return question

    @classmethod
    def parse_dict(cls, message, dct):
        question = cls(message)
        question.qname = Domain(dct.get('qname'), None)
        question.qtype = dct.get('qtype')
        question.qclass = dct.get('qclass')
        return question

    def __mydict__(self):
        dct = self.__dict__.copy()
        dct.pop('Binary')
        dct.pop('message')
        return dct

    @property
    def name(self):
        return self.qname

    @property
    def type(self):
        return self.qtype

    @property
    def cls(self):
        return self.qclass

    def __repr__(self):
        return str({'name': self.name,
                    'type': self.type,
                    'class': self.cls})


class QuestionStorage:
    class _Binary:
        def __init__(self, storage):
            self.storage = storage

        @property
        def full(self):
            result = ''
            for question in self.storage.storage:
                question_result = question.Binary.full
                # self.storage.message.offset += int(len(question_result) / 8)
                result += question_result
            return result

    def __init__(self, message):
        self.message = message
        self.storage = []
        self.Binary = self._Binary(self)

    def append(self, question: Question):
        assert isinstance(question, Question), f'What the heck is that {self.__class__.__name__.lower()}?'
        self.storage.append(question)

    @classmethod
    def parse_dict(cls, message, data):
        instance = cls(message)
        for x in data:
            instance.append(Question.parse_dict(message, x))
        return instance

    def __len__(self):
        return len(self.storage)

    def __bool__(self):
        return True if self.storage else False

    def __iter__(self):
        return (x for x in self.storage)

    def __getitem__(self, item):
        return self.storage[item]

    def __setitem__(self, key, value):
        self.storage[key] = value

    def __delitem__(self, key):
        self.storage.pop(key)

    def __repr__(self):
        return '[' + ','.join([a.__repr__() for a in self.storage]) + ']'
