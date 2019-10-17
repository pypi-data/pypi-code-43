import gevent
import gevent.monkey

gevent.monkey.patch_all()
import psycogreen.gevent

psycogreen.gevent.patch_psycopg()
import psycopg2
import os
from contextlib import contextmanager
from psycopg2 import pool, extras, errors  # pylint: disable=unused-import
import csv
import sqlalchemy.pool as pool
import pg8000


def getconn():
    c = pg8000.connect(
        host=os.environ["PGHOST"],
        port=5432,
        user=os.environ["PGUSER"],
        password=os.environ["PGPASSWORD"],
        database=os.getenv("PGDATABASE", "postgres"),
    )
    c.autocommit = True
    return c


class PostgresReader:
    """
    A simple library to help locust get and lock test data from a postgres database.
    the approach is fairly naive, dont expect it to scale to huge databases or heavy concurrency.

    This assumes you have a postgres database with a table similar to this: (using smallint instead of booleans for the logged_in flag is a historical accident). This may be all wrong, but maybe you can use it as a starting point.
    CREATE TABLE public.customers
    (
        account_id character(10) COLLATE pg_catalog."default",
        ssn character(12) COLLATE pg_catalog."default" NOT NULL,
        logged_in smallint NOT NULL DEFAULT '0'::smallint,
        last_login timestamp without time zone NOT NULL,
        CONSTRAINT customers_ssn UNIQUE (ssn)
    )
    CREATE INDEX customers_ssn_env_logged_in_last_login
        ON public.customers USING btree
        (ssn COLLATE pg_catalog."default" COLLATE pg_catalog."default", logged_in, last_login)
        TABLESPACE pg_default;
    """

    used = {}
    error_counter = 0

    def __init__(self, selection):
        """selection that will get appended to the where-clause, e.g. "some_column = 'some_value'" """
        # self._db = sqlalchemy.create_engine(
        #     sqlalchemy.engine.url.URL(
        #         drivername="postgres+pg8000",
        #         username=os.environ["PGUSER"],
        #         password=os.environ["PGPASSWORD"],
        #         database=os.getenv("PGDATABASE", "postgres"),
        #         host=os.environ["PGHOST"],
        #         port="5432",
        #     ),
        #     # Pool size is the maximum number of permanent connections to keep.
        #     pool_size=40,
        #     # Temporarily exceeds the set pool_size if no connections are available.
        #     max_overflow=0,
        #     # 'pool_timeout' is the maximum number of seconds to wait when retrieving a
        #     # new connection from the pool. After the specified amount of time, an
        #     # exception will be thrown.
        #     pool_timeout=1,  # 30 seconds
        #     # 'pool_recycle' is the maximum number of seconds a connection can persist.
        #     # Connections that live longer than the specified amount of time will be
        #     # reestablished
        #     pool_recycle=1800,  # 30 minutes
        #     poolclass=SingletonThreadPool,
        # )
        self._db = pool.SingletonThreadPool(getconn, pool_size=10, echo=True)
        self._selection = f" AND {selection}" if selection else ""

    def get(self):
        """Get and lock a customer by setting logged_in in an atomic db operation. Returns a dict."""

        conn = self._db.connect().cursor()
        proxy = conn.execute(
            f"UPDATE customers SET logged_in=1, last_login=now() WHERE ssn=(SELECT ssn FROM customers WHERE logged_in=0{self._selection} ORDER BY last_login LIMIT 1 FOR UPDATE SKIP LOCKED){self._selection} RETURNING *"
        )

        resp = proxy.fetchone()
        print(resp)
        if resp[1] in PostgresReader.used:
            print(f"{resp[1]} reused!")
            print(resp)
            # cursor.execute(f"SELECT * FROM customers WHERE ssn = '{resp[1]}'{self._selection}")
            # print(f"wtf {resp[1]}: {cursor.fetchone()}")
            os._exit(1)

        PostgresReader.used[resp[1]] = True
        conn.close()
        return resp

    def release(self, customer):
        """Unlock customer in database (set logged_in to zero)"""
        conn = self._db.connect().cursor()
        conn.execute(f"UPDATE customers SET logged_in=0 WHERE ssn='{customer[1]}'{self._selection}")
        conn.close()


class CSVReader:
    "Read test data from csv file using an iterator"

    def __init__(self, file):
        try:
            file = open(file)
        except TypeError:
            pass  # "file" was already a pre-opened file-like object
        self.file = file
        self.reader = csv.reader(file)

    def __next__(self):
        try:
            return next(self.reader)
        except StopIteration:
            # reuse file on EOF
            self.file.seek(0, 0)
            return next(self.reader)
