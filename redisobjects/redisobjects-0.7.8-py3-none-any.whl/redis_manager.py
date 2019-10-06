from .redis_keyspace import RedisKeyspace
from .redis_entity_space import RedisEntitySpace
from .redis_object_factory import RedisObjectFactory
from .redis_transaction import RedisTransaction
from .serializers import IdentitySerializer

from aioredis import create_connection

class RedisManager(RedisObjectFactory):
    def __init__(self, connection):
        RedisObjectFactory.__init__(self, connection)

    def keyspace(self, keyspace, key_serializer=IdentitySerializer()):
        return RedisKeyspace(self.connection, keyspace, key_serializer)

    '''
    Deprecated. Use RedisManager::entity_space instead.
    '''
    def object_space(self, keyspace, cls, *, key_serializer=IdentitySerializer()):
        return self.entity_space(keyspace, cls, key_serializer=key_serializer)

    def entity_space(self, keyspace, cls, *, key_serializer=IdentitySerializer()):
        return RedisEntitySpace(self.connection, keyspace, cls, key_serializer=key_serializer)

    def create_transaction(self):
        return RedisTransaction(self.connection)

    def close(self):
        self.connection.close()
