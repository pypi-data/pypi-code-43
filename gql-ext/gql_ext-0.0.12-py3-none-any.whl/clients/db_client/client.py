import ssl
from abc import ABC, abstractmethod
from typing import Union

import ujson
from asyncpg import Connection
from asyncpg.pool import Pool, create_pool
from ujson import dumps, loads

Con = Union[Pool, Connection]

__all__ = ('DBApi', 'DBRequest')


async def create_db_pool(dsn, **kwagrs) -> Pool:
    config = {**kwagrs, 'dsn': dsn}
    if kwagrs.get('ssl'):
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.load_verify_locations(kwagrs.get('ssl'))
        config['ssl'] = context
    return await create_pool(**config, init=_init_connection)


async def _init_connection(con: Connection):
    def _encoder(value):
        return b'\x01' + dumps(value).encode('utf-8')

    def _decoder(value):
        return loads(value[1:].decode('utf-8'))

    await con.set_type_codec(
        'jsonb',
        encoder=_encoder,
        decoder=_decoder,
        schema='pg_catalog',
        format='binary'
    )

    await con.set_type_codec(
        'json',
        encoder=ujson.dumps,
        decoder=ujson.loads,
        schema='pg_catalog',
    )


class DBApi:
    def __init__(self, pool: Con):
        self.pool = pool

    @classmethod
    async def create(cls, dsn, **kwargs):
        pool = await create_db_pool(dsn, **kwargs)
        return cls(pool)

    async def close(self):
        await self.pool.close()


class DBRequest(ABC):
    pool: Con

    def __get__(self, instance, owner):
        if instance is None:
            return self
        self.pool = instance.pool
        return self

    @abstractmethod
    async def __call__(self, **kwargs):
        pass
