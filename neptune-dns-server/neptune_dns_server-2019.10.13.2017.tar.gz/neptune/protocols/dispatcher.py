# from .._extentions.dnssec import sign_rrset
from neptune.connector import Connector
from triton.dns.edns import Edns
from triton.dns.message import Message
import json


class Dispatcher:
    able_to_truncate = False

    def __init__(self, loop, can_truncate=False):
        self.connector = Connector(loop)
        self.loop = loop
        self.can_truncate = can_truncate

    async def handle(self, raw_data):
        message = self.build_message(raw_data)
        Edns.procede(message)
        result_message = await self.resolve(message)
        return result_message.Binary.full

    async def not_in_cache(self, message, question):
        result = await self.connector.resolve(name=question.qname.label,
                                              type=question.qtype,
                                              cls=question.qclass)
        message.header._aa = 1
        if not result:
            # message.header._rcode = 3
            return message
        if isinstance(result, Message):
            message.add_dict(result.__dict__)
        else:
            message.add_dict(result)

    async def resolve(self, message):
        for question in message.question:
            if False:
                in_cache = await self.connector.cache_connector.Cache.get(name=question.qname.label,
                                                                          type=question.qtype,
                                                                          cls=question.qclass)
                if in_cache:
                    json_ = json.dumps(in_cache)
                    message.from_json(json_)
                    message.header._aa = 1
                    return message
                else:
                    await self.not_in_cache(message, question)
                    await self.connector.cache_connector.Cache.set(name=question.qname.label,
                                                                   type=question.qtype,
                                                                   cls=question.qclass,
                                                                   data=message.to_json())
            else:
                await self.not_in_cache(message, question)
                return message
        return message

    def build_message(self, raw_data):
        message = Message.parse_bytes(raw_data)
        return message
