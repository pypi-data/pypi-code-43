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
import array


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
        # self._pool = psycopg2.pool.SimpleConnectionPool(1, 20, host=os.environ["PGHOST"], port="5432")
        self._selection = f" AND {selection}" if selection else ""
        self.conns = {}

    def get(self):
        """Get and lock a customer by setting logged_in in an atomic db operation. Returns a dict."""
        gr = 0 if not hasattr(greenlet.getcurrent(), "minimal_ident") else greenlet.getcurrent().minimal_ident
        if not gr in self.conns:
            self.conns[gr] = psycopg2.connect(
                host=os.environ["PGHOST"], port="5432", cursor_factory=psycopg2.extras.DictCursor
            )

        conn = self.conns[gr].cursor()

        conn.execute(
            f"lock table customers in SHARE UPDATE EXCLUSIVE mode; UPDATE customers SET logged_in=1, last_login=now() WHERE ssn=(SELECT ssn FROM customers WHERE logged_in=0{self._selection} ORDER BY last_login LIMIT 1){self._selection} RETURNING account_id, ssn, last_login"
        )
        resp = conn.fetchone()
        self.conns[gr].commit()
        if resp[1] in PostgresReader.used:
            print(f"{resp[1]}")
            # # cursor.execute(f"SELECT * FROM customers WHERE ssn = '{resp[1]}'{self._selection}")
            # # print(f"wtf {resp[1]}: {cursor.fetchone()}")
            os._exit(1)

        conn.close()
        PostgresReader.used[resp[1]] = True

        return resp

    def release(self, customer):
        """Unlock customer in database (set logged_in to zero)"""
        gr = 0 if not hasattr(greenlet.getcurrent(), "minimal_ident") else greenlet.getcurrent().minimal_ident
        # print(f"releasing {customer[1]} associated with conn {gr}")

        conn = self.conns[gr].cursor()
        conn.execute(f"UPDATE customers SET logged_in=0 WHERE ssn='{customer[1]}'{self._selection} RETURNING ssn")
        resp = conn.fetchone()
        self.conns[gr].commit()
        conn.close()
        if resp[0] != customer[1]:
            raise Exception(f"failed to unlock customer with ssn {customer[1]}")


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
