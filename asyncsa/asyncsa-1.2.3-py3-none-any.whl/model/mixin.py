from sqlalchemy.sql import select
from sqlalchemy.ext.declarative import declared_attr
from ..util import get_logger
import logging
import os
import copy
logger = logging.getLogger(__package__)


class Mixin:

    d_values = {}
    _return_key = None

    @classmethod
    def return_key(cls):
        if not cls._return_key:
            for k in cls.__table__.columns:
                if hasattr(k, 'primary_key'
                           ) and getattr(k, 'primary_key'):
                    if getattr(k, 'primary_key'):
                        cls._return_key = k.name
            if not cls._return_key:
                cls._return_key = 'id'
        return cls._return_key

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    @classmethod
    def instancefy(cls, result=None):
        if isinstance(result, list):
            result = [cls(**item) for item in result]
        else:
            result = cls(**result)
        return result

    def to_dict(self):
        res = {k.name: getattr(self, k.name)
               for k in self.__table__.columns}
        return res

    async def save(self):
        await self.manager().instance(
            self, model=self.__class__, q_type='update')
        return self

    @staticmethod
    def handle_default_value(value):
        if callable(value):
            try:
                res = value()
            except Exception as tmp:
                print(tmp)
                res = value(None)
        else:
            res = value
        return res

    @classmethod
    def get_d_values(cls):
        if not cls.d_values:
            cls.d_values = {
                k.name: cls.handle_default_value(k.default.arg) for
                k in cls.__table__.columns
                if hasattr(k, 'default') and getattr(k, 'default')}
        return copy.deepcopy(cls.d_values)

    @classmethod
    async def create(cls, **kwargs):
        d_values = cls.get_d_values()
        d_values.update(kwargs)
        instance = cls(**d_values)
        resp = await cls.manager().instance(
            instance, model=cls, q_type='add', return_key=cls.return_key())
        if resp:
            data = resp[0]
        else:
            data = d_values
        result = await cls.get(**data)
        return result[-1]

    @classmethod
    async def get_one(cls, **kwargs):
        result = await cls.get(**kwargs)
        if len(result) > 0:
            return result[-1]
        else:
            return None

    @classmethod
    async def get(cls, **kwargs):
        result = await cls.manager().get_by_param(params=kwargs, model=cls)
        return cls.instancefy(result)

    async def delete(self, *args, **kwargs):
        await self.manager().instance(
            self, model=self.__class__, q_type='delete')
        return self.id or self.pk

    @classmethod
    async def all(cls):
        result = await cls.manager().all(model=cls)
        return cls.instancefy(result)

    @classmethod
    async def create_table(cls, Force=False):
        result = await cls.manager().create_table(model=cls, Force=Force)
        return result

    @classmethod
    def objects(cls, columns=None):
        if columns and isinstance(columns, list):
            return select(columns)
        else:
            return select([cls])

    @classmethod
    def manager(cls):
        if not cls._manager:
            raise Exception('model manager muset be set:_manager')
        return cls._manager
