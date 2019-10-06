from .redis_object import RedisObject
from .serializers import IdentitySerializer

'''
RedisList represents a linked list in Redis. This class supports push and pop operators,
among other typical list operators.
'''
class RedisList(RedisObject):
    def __init__(self, *, connection=None, key=None, serializer=IdentitySerializer()):
        RedisObject.__init__(self, connection=connection, key=key)
        self.serializer = serializer

    def _serialize_values(self, values):
        return [self.serializer.serialize(value) for value in values]

    async def add(self, *values, tx=None):
        tx = tx or self.connection
        return await self.push_right(tx, *values)

    async def push_right(self, *values, tx=None):
        tx = tx or self.connection
        return await tx.execute('rpush', self.key, *self._serialize_values(values))

    async def push_left(self, *values, tx=None):
        tx = tx or self.connection
        return await tx.execute('lpush', self.key, *self._serialize_values(values))

    async def items(self, limit=-1):
        results = await self.connection.execute('lrange', self.key, 0, limit)
        return (self.serializer.deserialize(value) for value in results)

    async def list(self, limit=-1):
        return list(await self.items(limit))

    async def pop_left(self):
        result = await self.connection.execute('lpop', self.key)
        return self.serializer.deserialize(result)

    async def pop_right(self):
        result = await self.connection.execute('rpop', self.key)
        return self.serializer.deserialize(result)

    async def remove(self, value, limit=1, *, tx=None):
        tx = tx or self.connection
        return await tx.execute('lrem', self.key, limit, self.serializer.serialize(value))

    async def size(self):
        return await self.connection.execute('llen', self.key)
