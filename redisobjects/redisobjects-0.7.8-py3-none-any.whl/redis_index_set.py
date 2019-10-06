from .redis_object import RedisObject
from .serializers import IdentitySerializer
from .redis_set import RedisSet
from .redis_atom import RedisAtom

class RedisIndexSet(RedisObject):
    def __init__(self, *, connection=None, key=None, index_space=None, serializer=IdentitySerializer()):
        RedisObject.__init__(self, connection=connection, key=key)
        self.index_space = index_space
        self.serializer = serializer
        self.set = RedisSet(self.connection, key, serializer)
        self.index = None

    async def initialize(self):
        members = await self.set.set()
        self.index = {member: self.index_space.atom(member) for member in members}

    async def add(self, *values, tx=None):
        tx = tx or self.connection
        await self.set.add(*values, tx=tx)
        for value in values:
            atom = self.index_space.atom(self.serializer.serialize(value))
            self.index[value] = atom
            await atom.set(self.key, tx=tx)

    async def remove(self, *values, tx=None):
        tx = tx or self.connection
        await self.set.remove(*values, tx=tx)
        for value in values:
            await self.index[value].remove(tx=tx)
            del self.index[value]

    async def items(self):
        return await self.set.items()
