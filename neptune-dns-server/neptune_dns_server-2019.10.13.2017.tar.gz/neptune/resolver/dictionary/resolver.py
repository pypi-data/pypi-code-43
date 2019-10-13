

type_int = {
    1: 'a',
    28: 'aaaa',
    15: 'mx'
}


class Resolver:

    def __init__(self, connection):
        self.connection = connection

    async def find(self, type, cls, name) -> dict:
        # TODO
        domain = self.connection.dictionary.get(name)
        if domain:
           for rr in domain.get(type_int[type]):
               print(rr)
        return {}