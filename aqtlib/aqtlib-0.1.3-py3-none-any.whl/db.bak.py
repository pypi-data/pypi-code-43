#!/usr/bin/env python3
#
# MIT License
#
# Copyright (c) 2019 Kelvin Gao
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import os
import asyncpg
import logging

from aqtlib.objects import Object
import aqtlib.util as util
import sqlalchemy as sa

from sqlalchemy.engine.url import URL

# from typing import List, Awaitable
from contextlib import asynccontextmanager

util.createLogger(__name__, logging.INFO)

"""
1. need create_engine?
2. how to construct query?
3. asyncpg.create_pool has loop ?
"""


class DataBase(Object):

    RequestTimeout = 0

    defaults = dict(
        dbname='aqtlib_db',
        user='aqtlib_user',
        password='aqtlib_pass',
        host='localhost'
    )
    __slots__ = list(defaults) + ['_engine', '_pool', '_logger']

    def __init__(self, *args, **kwargs):
        Object.__init__(self, *args, **kwargs)

        # self._dsn = dict(
        #     driver="postgres",
        #     database=self.dbname,
        #     user=self.user,
        #     password=self.password,
        #     host=self.host
        # )
        self._pool = None
        self._engine = None
        self._logger = logging.getLogger(__name__)

    @asynccontextmanager
    async def connection(self) -> asyncpg.Connection:
        if not self._pool:
            await self.connect()
        async with self._pool.acquire() as conn:
            yield conn

    async def connect(self) -> None:
        self._pool = await asyncpg.create_pool(
                        database=self.dbname,
                        user=self.user,
                        password=self.password,
                        host=self.host
                    )
        self._logger.info("PostgreSQL connected...")
        # await self.check_schema()

    async def check_schema(self):
        async with self.connection() as conn:
            records = await conn.fetch("SELECT * FROM pg_catalog.pg_tables \
                WHERE schemaname = 'public'")
            tables = [table[1] for table in records]

            required = ["ticks", "symbols"]
            if all(item in tables for item in required):
                return

            # create database schema
            basedir = os.path.dirname(__file__)
            with open(os.path.join(basedir, "schema.sql")) as f:
                schema = f.read()
            await conn.execute(schema)
            self._logger.info("Database schema created...")

    async def insert_row(self, tbl, **kwargs):
        async with self.connection() as conn:
            query = ticks.insert().values(**kwargs)
            return await conn.fetchrow(query)

    async def delete_row(self):
        pass

    def init_engine(self):
        self._engine = sa.create_engine(str(URL(
                        drivername='postgres',
                        database=self.dbname,
                        username=self.user,
                        password=self.password,
                        host=self.host
                    )))
        self._logger.info('Sqlalchemy engine created!')

    # SQL Alchemy Sync Operations
    def create_all(self) -> None:
        metadata.create_all(self._engine)
        self._logger.info('Sqlalchemy engine created all tables')

    # def drop_all(self) -> None:
    #     self._engine.execute(f'truncate {", ".join(sa.metadata.tables)}')
    #     try:
    #         self.engine.execute("drop table alembic_version")
    #     except Exception:  # noqa
    #         pass

    # def drop_all_schemas(self) -> None:
    #     self.engine.execute("DROP SCHEMA IF EXISTS public CASCADE")
    #     self.engine.execute("CREATE SCHEMA IF NOT EXISTS public")


metadata = sa.MetaData()

# AQTLib Schema Tables Definition
symbols = sa.Table(
    'symbols', metadata,
    sa.Column('id', sa.Integer(), primary_key=True),
    sa.Column('symbol', sa.String(24), nullable=True)
)

# ticks = sa.Table(
#     'custom_table', sa.MetaData(),
#     sa.Column('custom_id', sa.Integer(), primary_key=True),
#     sa.Column('payload'),
#     sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=text("now()"))
# )

# refs: https://github.com/quantmind/aio-openapi/blob/4136ab3b50f3c88966e607bce844eb7aef5cb0e0/openapi/db/container.py
