from .root import ChainResolver


class Resolver:

    def __init__(self, connection):
        self.connection = connection

    async def find(self, type: int, cls: int, name: str) -> dict:
        resolver = ChainResolver(name, type, custom_cache=self.connection.Cache)
        return await resolver.go()
