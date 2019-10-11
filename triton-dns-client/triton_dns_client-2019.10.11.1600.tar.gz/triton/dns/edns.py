from triton.dns.message import Answer
from triton.dns.message.rdata import OPT


class Edns:
    class _Binary:
        def __init__(self, edns):
            self.edns = edns

    _version = 1
    udp_size_limit = 4096
    dnssec = False

    def __init__(self, message):
        self.message = message

    @staticmethod
    def procede(message):
        for additional in message.additional:
            if isinstance(additional._rdata, OPT):
                instance = Edns(message)
                message._edns = instance
                instance.udp_payload_size = additional._cls
                raw_ttl = bin(additional._ttl)[2:].zfill(32)
                instance.extended_rcode = int(raw_ttl[:8], base=2)
                instance.version = int(raw_ttl[8:16], base=2)
                instance.do = int(raw_ttl[16], base=2)
                instance.z = int(raw_ttl[17:], base=2)
                message.additional.storage.clear()
                return instance
        message._edns = None
        return None

    async def check(self, new_message):
        self.new_message = new_message
        if self.udp_size_limit < len(new_message.Binary.full):
            raise Exception('SIZE is bigger than can handle')
        await self.inject()

    async def inject(self):
        answ = await Answer.parse_dict(self.new_message,
                                       {
                                           'name': '',
                                           'type': 41,
                                           'class': self.udp_size_limit,
                                           'ttl': int(
                                               f'{bin(self.extended_rcode)[2:].zfill(8)}{bin(self.version)[2:].zfill(8)}{bin(self.dnssec)[2:].zfill(1)}{bin(self.z)[2:].zfill(15)}',
                                               base=2),
                                           'rdata': {}
                                       }
                                       )
        self.new_message.additional.append(answ)
