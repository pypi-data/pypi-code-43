from .redis_object import RedisObject
from .serializers import IdentitySerializer

import aioredis

'''
RedisAtom represents a single key-value pair in a Redis database. Use the
async method get() to retrieve its value from the database and use the async method
set(x) to change its value to x.
'''
class RedisAtom(RedisObject):
    def __init__(self, *, connection=None, key=None, serializer=IdentitySerializer()):
        RedisObject.__init__(self, connection=connection, key=key)
        self.serializer = serializer

    async def get(self):
        value = await self.connection.execute('get', self.key)
        return self.serializer.deserialize(value)

    async def exists(self):
        return await self.connection.execute('exists', self.key) > 0

    async def set(self, value, *, tx=None):
        serialized_value = self.serializer.serialize(value)
        tx = tx or self.connection
        return await tx.execute('set', self.key, serialized_value)

    async def remove(self, *, tx=None):
        tx = tx or self.connection
        return await tx.execute('del', self.key) > 0
