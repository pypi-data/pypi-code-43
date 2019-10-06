from .serializers import IdentitySerializer, StringSerializer, TupleSerializer
from .redis_keyspace import RedisKeyspace
from .redis_atom import RedisAtom
from .redis_object import RedisObject
#from .redis_index_atom import RedisIndexAtom

import importlib
import uuid
from types import MethodType

class RedisEntitySpace:
    def __init__(self, db, keyspace, cls, *, key_serializer=IdentitySerializer(), key_factory=lambda: str(uuid.uuid4())):
        self.db = db
        self.keyspace = keyspace
        self.cls = cls
        self.key_serializer = key_serializer
        self.key_factory = key_factory
        self.cls_serializer = TupleSerializer.create_homogeneous(2, separator=':')
        self.indexes = {}

    def add_index(self, index, key_serializer=StringSerializer()):
        self.indexes[index] = RedisKeyspace('%s:__index__:%s:?' % (self.keyspace, index))

    async def create(self, cls=None, key=None):
        if cls is None:
            cls = self.cls
        if key is None:
            key = self.key_factory()
        obj = cls()
        self.hydrate(cls, obj, key)
        cls_atom = RedisAtom(connection=self.db, key=self.get_attribute_key(key, '__class__'), serializer=self.cls_serializer)
        await cls_atom.set((cls.__module__, cls.__name__))
        return obj

    async def remove(self, key, *, tx=None):
        obj = await self.get(key)
        if obj is None:
            return False
        return await obj.delete(tx=tx)

    def get_attribute_key(self, key, attribute):
        complete_key = '%s:%s:%s' % (self.keyspace, self.key_serializer.serialize(key), attribute)
        return complete_key

    def hydrate(self, cls, obj, key):
        obj._id = key
        for attribute, prop in obj.__dict__.items():
            complete_key = self.get_attribute_key(key, attribute)
            prop = getattr(obj, attribute)
            if isinstance(prop, RedisObject):
                prop.key = complete_key
                prop.connection = self.db
        obj.__class_atom__ = RedisAtom(connection=self.db, key=self.get_attribute_key(key, '__class__'), serializer=self.cls_serializer)
        async def delete(target, *, tx=None):
            for _, prop in obj.__dict__.items():
                if isinstance(prop, RedisObject):
                    await prop.delete(tx=tx)
        obj.delete = MethodType(delete, obj)
            # if isinstance(prop, RedisIndexAtom):
            #     prop.index_space =
            #setattr(obj, attribute, prop.map(self, attribute, self.db, complete_key, key))

    async def get_class(self, key):
        cls_atom = RedisAtom(connection=self.db, key=self.get_attribute_key(key, '__class__'), serializer=self.cls_serializer)
        if not await cls_atom.exists():
            return None
        module_name, cls_name = await cls_atom.get()
        cls = getattr(importlib.import_module(module_name), cls_name)
        if cls is None or not issubclass(cls, self.cls):
            return None
        return cls

    async def get(self, key):
        cls = await self.get_class(key)
        obj = None
        if cls is not None:
            obj = cls()
            self.hydrate(cls, obj, key)
        return obj

    '''
    Deprecated. Use RedisEntitySpace::get instead.
    '''
    async def object(self, key):
        return await self.get(key)

    async def get_index_atom(self, index, value):
        index_space = RedisKeyspace(self.db, '%s:__index__:%s:?' % (self.keyspace, index))
        index_atom = index_space.atom(value)
        return index_atom

    async def find(self, index, value):
        index_atom = await self.get_index_atom(index, value)
        if index_atom is None:
            return None
        key = await index_atom.get()
        if key is None:
            return None
        return await self.object(key.decode())
