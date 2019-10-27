import aiomysql
import logging
from .base import BaseConnection
from ..logger.logger import get_logger

logger = get_logger()

class AioMysql(BaseConnection):
    def __init__(self, conf=None):
        self.conf = conf
        self.init_pool = aiomysql.create_pool(
            host=conf.get('host', '127.0.0.1'), port=conf.get('port', 3306),
            user=conf.get('user', 'root'), password=conf.get('password', ''),
            db=conf.get('db', ''))
        self.pool = None

    async def connect(self,loop=None,**kwargs):
        self.pool = await aiomysql.create_pool(
            host=self.conf.get('host', '127.0.0.1'), port=self.conf.get('port', 3306),
            user=self.conf.get('user', 'root'), password=self.conf.get('password', ''),
            db=self.conf.get('db', ''),loop=loop,**kwargs)

    async def close(self):
        await self.pool.wait_closed()

    async def get(self, sql=None):
        try:
            async with self.pool.acquire() as con:
                async with con.cursor(aiomysql.DictCursor) as cur:
                    result = await cur.execute(sql)
                return result
        except Exception as tmp:
            logger.exception(tmp)

    async def set(self, sql=None):
        try:
            async with self.pool.acquire() as con:
                async with con.cursor(aiomysql.DictCursor) as cur:
                    result = await cur.execute(sql)
                    await con.commit()
                return result
        except Exception as tmp:
            logger.exception(tmp)

    async def bare_set(self, sql=None, con=None):
        try:
            async with con.cursor(aiomysql.DictCursor) as cur:
                result = await cur.execute(sql)
            return result
        except Exception as tmp:
            logger.exception(tmp)

    async def commit(self, con=None):
        await con.commit()
        self.pool.release(con)
        return True

    async def rollback(self, con=None):
        await con.rollback()

    async def get_transaction(self):
        con = await self.pool.acquire()
        return con
