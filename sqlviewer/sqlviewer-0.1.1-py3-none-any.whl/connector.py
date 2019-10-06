import os
import abc
import sqlite3
import psycopg2

from . import render

class Connector:

    ROWCOUNT = 80

    def __init__(self):
        self._engine = None

    @classmethod
    @abc.abstractclassmethod
    def setup(cls) -> dict:
        pass

    @abc.abstractmethod
    def execute(self, query: str):
        pass

    def serve(self):

        query = [] # Store various lines of sql query to be executed
        while True:
            # Hold connection open until the user indicates that they would like to break

            try:
                # Extract a line of the query
                sql = input('$ ')
                if not sql: continue # Empty - do nothing

                while ';' in sql:
                    query.append(sql[:sql.index(';')])

                    self.execute(' '.join(query))
                    query.clear()

                    sql = sql[sql.index(';') + 1:]

                query.append(sql)

            except Exception as e:
                print("Execution Error: {}".format(e))

            except KeyboardInterrupt:
                print()
                break

class SQLiteConnector(Connector):

    def __init__(self, location):
        self._engine = sqlite3.connect(location)

    @classmethod
    def setup(cls):

        while True:
            location = input('Filepath: ')
            print()
            exists = os.path.exists(location)

            try:
                cls(location)
                if not exists: print('WARNING: no database existed at the location specified')
                return {'location': os.path.abspath(os.path.expanduser(location))}
            except Exception as e:
                print("Couldn't create connection to database because {}".format(e))
                print('Please try again\n')


    def execute(self, query: str):

        result = self._engine.execute(query)

        if result.description is not None:
            columns = [x[0] for x in result.description]
            rows = result.fetchmany(self.ROWCOUNT)
            render.table(columns, rows)

class PostgresConnector(Connector):

    def __init__(self, **kwargs):
        self._engine = psycopg2.connect(**kwargs)

    def __del__(self):
        if hasattr(self, '_engine'):
            self._engine.close()

    @classmethod
    def setup(cls):

        while True:
            print("Creating connection variables for Postgres... Leave entries blank for None.")

            config = {
                'host': input('host: '),
                'port': input('port: '),
                'user': input('user: '),
                'password': input('password: '),
                'dbname': input('dbname: ')
            }

            try:
                cls(**config)
                return config
            except Exception as e:
                print("Couldn't create connection to database because {}".format(e))
                print('please try again.')

    def execute(self, query: str):
        conn = self._engine.cursor()

        try:
            conn.execute(query)
            self._engine.commit()

            if conn.description:
                columns = [x.name for x in conn.description]
                rows = conn.fetchmany(self.ROWCOUNT)
                render.table(columns, rows)

        except:
            raise
        finally:
            conn.close()