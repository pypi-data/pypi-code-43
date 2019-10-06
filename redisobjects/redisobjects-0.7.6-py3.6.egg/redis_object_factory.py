from .serializers import IdentitySerializer
from .redis_atom import RedisAtom
from .redis_list import RedisList
from .redis_dict import RedisDict
from .redis_set import RedisSet

class RedisObjectFactory:
    def __init__(self, connection):
        self.connection = connection

    def _make_key(self, key):
        return key

    def atom(self, key, serializer=IdentitySerializer()):
        return RedisAtom(connection=self.connection, key=self._make_key(key), serializer=serializer)

    def integer(self, key, serializer=IdentitySerializer()):
        return RedisInteger(connection=self.connection, key=self._make_key(key), serializer=serializer)

    def list(self, key, serializer=IdentitySerializer()):
        return RedisList(connection=self.connection, key=self._make_key(key), serializer=serializer)

    def dict(self, key, value_serializer=IdentitySerializer(), field_serializer=IdentitySerializer()):
        return RedisDict(connection=self.connection, key=self._make_key(key), value_serializer=value_serializer, field_serializer=field_serializer)

    def set(self, key, serializer=IdentitySerializer()):
        return RedisSet(connection=self.connection, key=self._make_key(key), serializer=erializer)
