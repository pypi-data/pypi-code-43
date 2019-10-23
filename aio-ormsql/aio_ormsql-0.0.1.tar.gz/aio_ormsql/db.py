from typing import AsyncGenerator, Union, Any

import aiomysql

from .classes import WHERE, Query, _prepare_string, _escape


class DataBase:
    def __init__(self, user: str, password: str, db: str, table: str = '',
                 host: str = 'localhost', port: int = 3306,
                 cursor: aiomysql.Cursor = aiomysql.SSCursor):
        '''
            user - mysql user\n
            password - mysql user password\n
            db - mysql database name\n
            table - mysql database table name\n
            host - mysql host\n
            port - mysql port\n
            cursor  - mysql cursor type
        '''

        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.table = table
        self.db = db
        self.cursor = cursor

    def _check_special(self, what: Any) -> str:
        special = ('*', 'COUNT', 'UNIQUE')

        if not isinstance(what, str):
            return str(what)
        elif what.startswith(special):
            return str(what)
        else:
            return f'`{what}`'

    async def connect(self, **kwargs) -> None:
        '''
            Connect to database
        '''

        self.pool = await aiomysql.create_pool(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            db=self.db,
            cursorclass=self.cursor,
            **kwargs
        )

    async def close(self) -> None:
        '''
            Close connection and wait for tasks end
        '''

        self.pool.close()
        await self.pool.wait_closed()

    async def fetch_gen(self, sql: Union[str, Query]) -> AsyncGenerator:
        '''
            Return async-generator for fetching lines from database\n
            Must have default cursor.
        '''

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(sql)

                while True:
                    row = await cur.fetchone()

                    if not row:
                        break

                    yield row

    async def fetchall(self, sql: Union[str, Query]) -> tuple:
        '''
            Fetch all results from database by SQL query
        '''

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(sql)
                return await cur.fetchall()

    async def put(self, sql: Union[str, Query]) -> None:
        '''
            Execute SQL without return answer
        '''

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(sql)
                await conn.commit()

    async def select(self, what: list, distinct: bool = True,
                     where: WHERE = '', additional: str = '',
                     table: Union[str, Query] = '', back: bool = False
                     ) -> Union[Query, tuple]:
        '''
            what - list of items what you want select\n
            distinct - select unique rows?\n
            where - WHERE statement\n
            additional - you can put something like a: LIMIT 10, etc\n
            table - table name or left empty if you set in init\n
            back - just back a SQL statement
        '''

        table = table if table else self.table

        statement = 'SELECT' + (' DISTINCT' if distinct else '') + ' '
        statement += ', '.join(map(self._check_special, what))
        statement += ' FROM '

        if isinstance(table, Query):
            statement += f'({table})'
        else:
            statement += f'`{table}`'

        if where:
            statement += ' '+str(where)

        if additional:
            statement += ' '+additional

        if back:
            return Query(statement)

        return await self.fetchall(statement)

    async def insert(self, what: dict, table: str = '',
                     additional: str = '', back: bool = False) -> tuple:
        '''
            what - name:value pairs for insert\n
            table - table name or left empty if you set in init\n
            additional - you can put something like a: LIMIT 10, etc\n
            back - just back a SQL statement
        '''

        names = []
        values = []
        table = table if table else self.table

        for name, value in what.items():
            names.append(str(name))
            values.append(value)

        statement = f'INSERT INTO `{table}` (`'+'`, `'.join(names)
        statement += '`) VALUES ('
        cleared = []

        for value in values:
            if isinstance(value, str):
                cleared.append(_escape(value))
            else:
                cleared.append(str(value))

        statement += ', '.join(cleared)
        statement += ')'

        if additional:
            statement += ' '+additional

        if back:
            return Query(statement)

        return await self.put(statement)

    async def update(self, pairs: dict, where: WHERE = '', table: str = '',
                     additional: str = '', back: bool = False) -> tuple:
        '''
            pairs - name:value pairs for insert\n
            where - WHERE statement\n
            table - table name or left empty if you set in init\n
            additional - you can put something like a: LIMIT 10, etc\n
            back - just back a SQL statement
        '''

        table = table if table else self.table

        statement = f'UPDATE `{table}` SET '
        statement += ', '.join(_prepare_string(pairs))

        if where:
            statement += ' '+str(where)

        if additional:
            statement += ' '+additional

        if back:
            return Query(statement)

        return await self.put(statement)
