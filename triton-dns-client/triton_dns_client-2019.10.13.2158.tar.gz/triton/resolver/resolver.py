from .root import ChainResolver
import triton


class Resolver:

    def __init__(self, connection):
        self.connection = connection

    async def find(self, type: int, cls: int, name: str) -> dict:
        resolver = ChainResolver(name, type, cls, custom_cache=self.connection.Cache, loop=self.connection.loop)
        result = await resolver.go()
        if result:
            for answer in result.answer:
                if isinstance(answer.rdata, triton.dns.message.rdata.CNAME):
                    for answer_ in (await self.find(type=1, name=answer.rdata.cname.label, cls=1)).answer:
                        if answer_.name.lower() == answer.rdata.cname.label.lower():
                            result.answer.append(answer_)
            return result
        else:
            return triton.dns.Message.create_question(name, type, cls)

