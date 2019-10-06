from .serializers import IdentitySerializer
from .redis_object_factory import RedisObjectFactory

from shortuuid import uuid

'''
A RedisKeyspace is a subspace in a Redis database represented by a key with placeholders and a key serializer
that converts key objects to strings. For example, if I want to store lists of Entity objects at (x,y,z) point coordinates in a
Redis database, then I could pass to world:entities:? to the RedisKeyspace with a serializer that converts (x,y,z) tuples to
x,y,z strings as follows (assume that the variable redis is the RedisManager):

entities = [e1, e2, ...]
entity_serializer = ...
xyz = (x,y,z)
subspace = redis.keyspace('world:entities:?', TupleSerializer.create_homogeneous(3))
entities_at_xyz = subspace.list(xyz, entity_serializer)
entities_at_xyz.push_right(*entities)

This may seem overly complex, but the main benefit is being able to reuse and pass aroud this keyspace.
'''
class RedisKeyspace(RedisObjectFactory):
    def __init__(self, connection, keyspace='?', key_serializer=IdentitySerializer(), key_factory=lambda: str(uuid())):
        RedisObjectFactory.__init__(self, connection)
        self.key_serializer = key_serializer
        self.placeholder = '?'
        self.keyspace = keyspace
        self.key_factory = key_factory

    def _make_key(self, key=None):
        if key is None:
            key = self.key_factory()
        serialized_key = self.key_serializer.serialize(key)
        complete_key = self.keyspace.replace(self.placeholder, serialized_key)
        if self.placeholder in complete_key:
            raise RuntimeError('Not all placeholders have been replaced for `%s`' % (complete_key,))
        return complete_key
