import asyncio
from sqlalchemy.schema import CreateTable, DropTable
from asyncsa.connection.async_pg import AsyncPg
from .base import BaseManager
import logging
logger = logging.getLogger(__package__)


class PostgresManager(BaseManager):
    def __init__(self, conf=None):
        dsn = conf.get('dsn')
        if not dsn:
            raise Exception('dsn dosnot exist')
        self.connection = AsyncPg(dsn=dsn)

    async def connect(self, loop=None, **kwargs):
        await self.connection.connect(loop=loop, **kwargs)

    async def close(self):
        await self.connection.close()

    async def create_table(self, model=None, Force=False):
        try:
            if Force:
                sql_string = str(DropTable(model.__table__))
                await self.connection.set(sql_string)
            sql_string = str(CreateTable(model.__table__))
            await self.connection.set(sql_string)
            result = True
        except Exception as tmp:
            print(tmp)
            result = False
        return result

    async def get_by_param(self, params=None, model=None):
        query_judge = None
        for k, v in params.items():
            if hasattr(model.__table__.c, k):
                if query_judge is not None:
                    query_judge = query_judge & (
                        getattr(model.__table__.c, k) == v)
                else:
                    query_judge = (
                        getattr(model.__table__.c, k) == v)
        query = model.__table__.select().where(query_judge)
        print(type(query))
        sql_string = self.format_query(query=query)
        print(sql_string)
        result = await self.connection.get(sql_string)
        return result

    async def get(self, query=None):
        sql_string = self.format_query(query=query)
        result = await self.connection.get(sql_string)
        return result

    async def set(self, query=None, model=None, q_type=None, return_key=None):
        if return_key is None:
            return_key = 'id'
        sql_string = self.format_query(query=query)
        if q_type == 'add':
            sql_string += f' RETURNING {return_key}'
        print(sql_string)
        result = await self.connection.set(sql_string)
        return result

    def format_query(self, query=None):
        return str(query.compile(
            compile_kwargs={"literal_binds": True}))

    async def set_multi(self, query_list=None, model=None):
        con, tr = await self.connection.get_transaction()
        sql_list = [self.format_query(query=query) for query in query_list]
        task_list = [self.connection.bare_set(
            sql=sql, con=con) for sql in sql_list]
        aa = await asyncio.wait(task_list)
        if aa[-1]:
            await self.connection.rollback(con=con, tr=tr)
            return False
        else:
            await self.connection.commit(con=con, tr=tr)
            return True

    async def all(self, model=None):
        query = model.__table__.select()
        return await self.get(query=query)

    async def instance(self, instance=None, model=None,
                       q_type=None, return_key=None):
        values = {k: v for k,
                  v in instance.__dict__.items() if not k.startswith('_')}

        if q_type == 'add':
            query = model.__table__.insert().values(
                **values)
        elif q_type == 'delete':
            query = model.__table__.delete().where(
                model.id == instance.id)
        else:
            query = model.__table__.update().where(
                model.id == instance.id).values(
                **values)
        return await self.set(query=query, q_type=q_type,
                              return_key=return_key)

    async def execute(self, sql_string=None, read=True, transaction=False):
        if read:
            result = await self.connection.get(sql_string)
        else:
            if transaction:
                con, tr = await self.connection.get_transaction()
                try:
                    result = await self.connection.bare_set(
                        sql=sql_string, con=con)
                except Exception as tmp:
                    result = False
                if result:
                    await self.connection.commit(con=con, tr=tr)
                    return result
                else:
                    await self.connection.rollback(con=con, tr=tr)
                    return result
            else:
                try:
                    result = await self.connection.set(
                        sql=sql_string)
                except Exception as tmp:
                    raise Exception(tmp)
        return result
