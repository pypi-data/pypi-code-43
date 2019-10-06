from .redis_object import RedisObject
from .serializers import IdentitySerializer

class RedisSet(RedisObject):
	def __init__(self, *, connection=None, key=None, value_serializer=IdentitySerializer()):
		RedisObject.__init__(self, connection=connection, key=key)
		self.value_serializer = value_serializer

	def _serialize_values(self, values):
		return [self.value_serializer.serialize(value) for value in values]

	def _deserialize_values(self, values):
		return [self.value_serializer.deserialize(value) for value in values]

	async def _apply_set_operator(self, op, *redis_sets):
		keys = [redis_set.key for redis_set in redis_sets]
		results = await self.connection.execute(op, self.key, *keys)
		return self._deserialize_values(results)

	async def add(self, *values, tx=None):
		tx = tx or self.connection
		serialized_values = self._serialize_values(values)
		return await tx.execute('sadd', self.key, *serialized_values)

	async def remove(self, *values, tx=None):
		tx = tx or self.connection
		serialized_values = self._serialize_values(values)
		return await tx.execute('srem', self.key, *serialized_values)

	async def items(self):
		results = await self.connection.execute('smembers', self.key)
		return self._deserialize_values(results)

	async def set(self):
		return set(await self.items())

	async def intersect(self, *redis_sets):
		return await self._apply_set_operator('sinter', *redis_sets)

	async def union(self, *redis_sets):
		return await self._apply_set_operator('sunion', *redis_sets)

	async def diff(self, *redis_sets):
		return await self._apply_set_operator('sdiff', *redis_sets)

	async def contains(self, *values):
		serialized_values = self._serialize_values(values)
		result = await self.connection.execute('sismember', self.key, *serialized_values)
		return result == len(values)

	async def size(self):
		return await self.connection.execute('scard', self.key)

	async def choose(self, n=1, distinct=True):
		n = n if distinct else (-1 * abs(n))
		results = await self.connection.execute('srandmember', self.key, n)
		return self._deserialize_values(results)

	async def pop(self, n=1):
		results = await self.connection.execute('spop', self.key, n)
		return self._deserialize_values(results)

	async def move(self, value, redis_set, *, tx=None):
		tx = tx or self.connection
		serialized_value = self.value_serializer.serialize(value)
		return await tx.execute('smove', self.key, redis_set.key, serialized_value)
