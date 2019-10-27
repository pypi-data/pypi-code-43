import asyncpg
from .base import BaseConnection
from ..logger.logger import get_logger

logger = get_logger()

class AsyncPg(BaseConnection):
    def __init__(self, dsn=None):
        self.dsn = dsn
        self.pool = None

    async def connect(self,loop=None,**kwargs):
        self.pool = await asyncpg.create_pool(dsn=self.dsn, loop=loop, **kwargs)

    async def close(self):
        await self.pool.close()

    def format_sql_result(self, result=None):
        if isinstance(result, list):
            result = [dict(i) for i in result]
        else:
            try:
                result = dict(result)
            except Exception as tmp:
                logger.exception(tmp)
                result = result
        return result

    async def get(self, sql=None):
        try:
            async with self.pool.acquire() as con:
                result = await con.fetch(sql)
                return self.format_sql_result(result=result)
        except Exception as tmp:
            logger.exception(tmp)
            raise Exception(tmp)

    async def set(self, sql=None):
        try:
            async with self.pool.acquire() as con:
                result = await con.fetch(sql)
                return self.format_sql_result(result=result)
        except Exception as tmp:
            logger.exception(tmp)
            raise Exception(tmp)

    async def bare_set(self, sql=None, con=None):
        try:
            result = await con.execute(sql)
            return self.format_sql_result(result=result)
        except Exception as tmp:
            logger.exception(tmp)
            raise Exception(tmp)

    async def commit(self, con=None, tr=None):
        await tr.commit()
        await self.pool.release(con)
        return True

    async def rollback(self, con=None, tr=None):
        await tr.rollback()
        await self.pool.release(con)

    async def get_transaction(self):
        con = await self.pool.acquire()
        self._tr_con = con
        tr = con.transaction()
        await tr.start()
        return con, tr
