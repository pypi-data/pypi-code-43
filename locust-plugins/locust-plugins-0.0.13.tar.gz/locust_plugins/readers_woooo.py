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
import greenlet

POOL_SIZE = 40
from gevent.lock import Semaphore

sem = Semaphore()


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

    def __init__(self, selection):
        """selection that will get appended to the where-clause, e.g. "some_column = 'some_value'" """
        self._pool = psycopg2.pool.SimpleConnectionPool(
            1, POOL_SIZE, host=os.environ["PGHOST"], port="5432", cursor_factory=psycopg2.extras.DictCursor
        )
        self._selection = f" AND {selection}" if selection else ""

    used = {}

    def get(self):
        """Get and lock a customer by setting logged_in in an atomic db operation. Returns a dict."""
        sem.acquire()
        with self.db() as conn:
            current_greenlet = greenlet.getcurrent()  # pylint: disable=I1101
            if hasattr(current_greenlet, "minimal_ident"):
                greenlet_id = current_greenlet.minimal_ident
            else:
                greenlet_id = -1  # if no greenlet has been spawned (typically when debugging)

            print(f"about to get with {greenlet_id}, {conn}")

            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE customers SET logged_in=1, last_login=now() WHERE ssn=(SELECT ssn FROM customers WHERE logged_in=0{self._selection} ORDER BY last_login LIMIT 1){self._selection} RETURNING account_id, ssn, last_login"
            )
            resp = cursor.fetchone()
            cursor.close()
            conn.commit()
            sem.release()
            if hasattr(current_greenlet, "minimal_ident"):
                greenlet_id = current_greenlet.minimal_ident
            else:
                greenlet_id = -1  # if no greenlet has been spawned (typically when debugging)

            print(f"aquired {resp[1]}, {resp[2]} with {greenlet_id}, {conn}")
            if resp[1] in PostgresReader.used:
                print(f"{resp[1]}")
                # # cursor.execute(f"SELECT * FROM customers WHERE ssn = '{resp[1]}'{self._selection}")
                # # print(f"wtf {resp[1]}: {cursor.fetchone()}")
                os._exit(1)

        PostgresReader.used[resp[1]] = True

        return resp

    def release(self, customer):
        """Unlock customer in database (set logged_in to zero)"""
        with self.db() as conn:
            current_greenlet = greenlet.getcurrent()  # pylint: disable=I1101
            if hasattr(current_greenlet, "minimal_ident"):
                greenlet_id = current_greenlet.minimal_ident
            else:
                greenlet_id = -1  # if no greenlet has been spawned (typically when debugging)

            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE customers SET logged_in=0 WHERE ssn='{customer['ssn']}' AND last_login='{customer['last_login']}' AND logged_in=1{self._selection} RETURNING ssn"
            )
            print(f"released {customer[1]} with {greenlet_id}, {conn}")
            resp = cursor.fetchone()
            print(f"resp for {customer[1]} was {resp[0]}")
            cursor.close()
            conn.commit()

    @contextmanager
    def db(self):
        current_greenlet = greenlet.getcurrent()  # pylint: disable=I1101
        if hasattr(current_greenlet, "minimal_ident"):
            greenlet_id = current_greenlet.minimal_ident
        else:
            greenlet_id = -1  # if no greenlet has been spawned (typically when debugging)
        conn = self._pool.getconn(greenlet_id % POOL_SIZE)
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        try:
            yield conn
        finally:
            self._pool.putconn(conn, greenlet_id % POOL_SIZE)


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
