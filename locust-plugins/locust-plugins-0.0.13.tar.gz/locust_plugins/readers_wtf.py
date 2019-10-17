import gevent
import gevent.monkey

gevent.monkey.patch_all()
import psycogreen.gevent

psycogreen.gevent.patch_psycopg()
import psycopg2
import os
from contextlib import contextmanager
from psycopg2 import pool, extras  # pylint: disable=unused-import
import csv
import greenlet
import time


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

    def __init__(self, selection):
        """selection that will get appended to the where-clause, e.g. "some_column = 'some_value'" """
        self._conn = psycopg2.connect(
            host=os.environ["PGHOST"], port="5432", cursor_factory=psycopg2.extras.RealDictCursor
        )
        self._selection = f" AND {selection}" if selection else ""

    def get(self):
        """Get and lock a customer by setting logged_in in an atomic db operation. Returns a dict."""
        cursor = self._conn.cursor()
        cursor.execute(
            f"UPDATE customers SET logged_in=1, last_login=now() WHERE ssn=(SELECT ssn FROM customers WHERE logged_in=0{self._selection} ORDER BY last_login LIMIT 1 FOR UPDATE SKIP LOCKED){self._selection} RETURNING account_id, ssn, last_login"
        )
        resp = cursor.fetchone()
        print(f"aquired {resp['ssn']}, {resp['last_login']} with {greenlet.getcurrent().minimal_ident}")
        cursor.close()
        if resp["ssn"] in PostgresReader.used:
            print(f"{resp['ssn']} reused!")
            # cursor.execute(f"SELECT * FROM customers WHERE ssn = '{resp[1]}'{self._selection}")
            # print(f"wtf {resp[1]}: {cursor.fetchone()}")
            os._exit(1)

        PostgresReader.used[resp["ssn"]] = True

        return resp

    def release(self, customer):
        """Unlock customer in database (set logged_in to zero)"""
        cursor = self._conn.cursor()
        print(f"releasing {customer['ssn']} associated with conn {greenlet.getcurrent().minimal_ident}")
        cursor.execute(f"UPDATE customers SET logged_in=0 WHERE ssn='{customer['ssn']}'{self._selection} RETURNING ssn")
        ssn = cursor.fetchone()["ssn"]
        cursor.close()
        if ssn != customer["ssn"]:
            raise Exception(f"failed to unlock customer with ssn {ssn}")

    @contextmanager
    def _getcursor(self) -> psycopg2.extras.DictCursor:
        pass
        # conn = self._pool.getconn()
        # # conn.autocommit = True
        # try:
        #     cursor = conn.cursor(withold=True)
        #     cursor.myconn = conn
        #     yield cursor
        # finally:
        #     time.sleep(0.1)
        #     self._pool.putconn(conn, close=True)


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
