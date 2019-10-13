class Header:
    class _Binary:

        def __init__(self, header):
            self.header = header

        @property
        def full(self):
            result = bin(self.header._id)[2:].zfill(16)
            result += bin(self.header.qr)[2:].zfill(1)
            result += bin(self.header._opcode)[2:].zfill(4)
            result += bin(self.header._aa)[2:].zfill(1)
            result += bin(self.header._tc)[2:].zfill(1)
            result += bin(self.header._rd)[2:].zfill(1)
            result += bin(self.header._ra)[2:].zfill(1)
            result += bin(self.header._z)[2:].zfill(3)
            result += bin(self.header._rcode)[2:].zfill(4)
            result += bin(self.header.qdcount)[2:].zfill(16)
            result += bin(self.header.ancount)[2:].zfill(16)
            result += bin(self.header.nscount)[2:].zfill(16)
            result += bin(self.header.arcount)[2:].zfill(16)
            self.header.message.offset = 12
            return result

    def __init__(self, message):
        self.Binary = self._Binary(self)
        self.message = message

    @classmethod
    def parse_bytes(cls, message):
        header = cls(message)
        header._id = message.stream.read('uint:16')
        header._qr = message.stream.read('uint:1')
        header._opcode = message.stream.read('uint:4')
        header._aa = message.stream.read('uint:1')
        header._tc = message.stream.read('uint:1')
        header._rd = message.stream.read('uint:1')
        header._ra = message.stream.read('uint:1')
        header._z = message.stream.read('uint:3')
        header._rcode = message.stream.read('uint:4')
        header._qdcount = message.stream.read('uint:16')
        header._ancount = message.stream.read('uint:16')
        header._nscount = message.stream.read('uint:16')
        header._arcount = message.stream.read('uint:16')
        return header

    @classmethod
    def parse_dict(cls, message, data):
        header = cls(message)
        header._id = data.get('id')
        header._qr = data.get('qr')
        header._opcode = data.get('opcode')
        header._aa = data.get('aa')
        header._tc = data.get('tc')
        header._rd = data.get('rd')
        header._ra = data.get('ra')
        header._z = data.get('z')
        header._rcode = data.get('rcode')
        header._qdcount = data.get('qdcount')
        header._ancount = data.get('ancount')
        header._nscount = data.get('nscount')
        header._arcount = data.get('arcount')
        return header

    @property
    def qr(self):
        return 1 if (bool(self.message.answer) or bool(self.message.authority)) else 0

    @property
    def qdcount(self):
        return len(self.message.question)

    @property
    def ancount(self):
        return len(self.message.answer)

    @property
    def nscount(self):
        return len(self.message.authority)

    @property
    def arcount(self):
        return len(self.message.additional)

    def __mydict__(self):
        return {'id': self._id,
                'qr': self.qr,
                'opcode': self._opcode,
                'aa': self._aa,
                'tc': self._tc,
                'rd': self._rd,
                'ra': self._ra,
                'z': self._z,
                'rcode': self._rcode,
                'qdcount': self.qdcount,
                'ancount': self.ancount,
                'nscount': self.nscount,
                'arcount': self.arcount}

    def __repr__(self):
        return str(self.__mydict__())
