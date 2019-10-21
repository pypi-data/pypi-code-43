import sys
import sqlite3
import logging
from time import time

logger = logging.getLogger('pagespeed')


class SQLiteData:
    def __init__(self, db_name: str = None):
        try:
            if db_name is None:
                raise ValueError("No database name")

            self.db_name = db_name
            self.conn = None
            self.cursor = None

        except ValueError as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error(f"{str(exc_type)} :: {str(exc_tb.tb_lineno)} :: {e}")
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.warning(f"{str(exc_type)} :: {str(exc_tb.tb_lineno)} :: {e}")

    def connect(self):
        try:
            if self.conn is None:
                raise Exception("We have no connection!")

            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.warning(f"{str(exc_type)} :: {str(exc_tb.tb_lineno)} :: {e}")

    def create_table(self, table_name: str = None, table: dict = None):
        sql = ""
        try:
            if table_name is None:
                raise ValueError("No table name")
            if table is None or not isinstance(table, dict):
                raise ValueError("No correct table dictionary")

            columns = "(" + ",\n".join(["{} {}".format(k, v) for k, v in table.items()]) + ")"

            with sqlite3.connect(self.db_name, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
                cursor = conn.cursor()
                sql = f"CREATE TABLE IF NOT EXISTS {table_name} {columns}"
                cursor.execute(sql)
                conn.commit()

            return True

        except ValueError as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error(f"{str(exc_type)} :: {str(exc_tb.tb_lineno)} :: {e} :: {sql}")
            return False
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.warning(f"{str(exc_type)} :: {str(exc_tb.tb_lineno)} :: {e} :: {sql}")
            return False

    def check_table_exists(self, table: str = None):
        try:
            if table is None:
                return False
            with sqlite3.connect(self.db_name, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
                cursor = conn.cursor()
                sql = f"SELECT name FROM sqlite_master WHERE type='table' AND name={t_name};"
                # if the count is 1, then table exists
                cursor.execute(sql)

                if cursor.fetchone()[0] == 1:
                    return True

                return False
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.warning(f"{str(exc_type)} :: {str(exc_tb.tb_lineno)} :: {e} :: {sql}")
            return False

    def insert_into_table(self, table_name: str = None, table_data: dict = None):
        sql = ""
        try:
            if table_name is None:
                raise ValueError("No table name")
            if table_data is None or not isinstance(table_data, dict):
                raise ValueError("No correct table data dictionary")

            columns = ', '.join(table_data.keys())
            placeholders = ':' + ', :'.join(table_data.keys())

            with sqlite3.connect(self.db_name, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
                cursor = conn.cursor()
                sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
                cursor.execute(sql, tuple(table_data.values()))
                conn.commit()

            return True

        except ValueError as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error(f"{str(exc_type)} :: {str(exc_tb.tb_lineno)} :: {e} :: {sql}")
            return False
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.warning(f"{str(exc_type)} :: {str(exc_tb.tb_lineno)} :: {e} :: {sql}")
            return False

    def select_from_table(self, table_name: str = None, where_data: dict = None, fetch: str = 'all'):
        sql = ""
        try:
            if table_name is None:
                raise ValueError("No table name")
            if where_data is None or not isinstance(where_data, dict):
                raise ValueError("No correct table data dictionary")

            columns = 'AND '.join(f"{k} = ? " for k, v in where_data.items())
            placeholders = ':' + ', :'.join(where_data.keys())

            with sqlite3.connect(self.db_name, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
                cursor = conn.cursor()
                sql = f"SELECT * FROM {table_name} WHERE {columns}"

                cursor.execute(sql, tuple(where_data.values()))
                if fetch == 'all':
                    return cursor.fetchall()
                else:
                    return cursor.fetchone()

        except ValueError as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error(f"{str(exc_type)} :: {str(exc_tb.tb_lineno)} :: {e} :: {sql}")
            return False
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.warning(f"{str(exc_type)} :: {str(exc_tb.tb_lineno)} :: {e} :: {sql}")
            return False

    def drop_table(self, table_name: str = None):
        try:
            if table_name is None:
                raise ValueError("No table name")
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(f"DROP TABLE {table_name}")
                conn.commit()

            return True

        except ValueError as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error(f"{str(exc_type)} :: {str(exc_tb.tb_lineno)} :: {e}")
            return False
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.warning(f"{str(exc_type)} :: {str(exc_tb.tb_lineno)} :: {e}")
            return False

    def close(self):
        try:

            self.conn.close()
            return True
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.warning(f"{str(exc_type)} :: {str(exc_tb.tb_lineno)} :: {e}")
            return False


if __name__ == '__main__':
    dbname = "../data/test.sqlite"
    sld = SQLiteData(dbname)

    t_name = "coins"
    coin_table = {
            'id': "INTEGER PRIMARY KEY",
            'coin': 'TEXT',
            'aks_bid': 'TEXT',
            'timestamp': 'INTEGER',
            'value': 'decimal',
            'amount': 'INTEGER'}

    sld.create_table(t_name, coin_table)

    coin_values = {'coin': 'LTO',
                   'aks_bid': 'bid',
                   'timestamp': int(time()),
                   'value': 0.052321,
                   'amount': 200}

    sld.insert_into_table(t_name, coin_values)
