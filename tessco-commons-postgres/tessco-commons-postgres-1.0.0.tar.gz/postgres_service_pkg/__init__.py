import psycopg2
from psycopg2.extras import RealDictCursor


class PostgresService:
    def __init__(self, host, username, password, name, schema, port):
        self.host = host
        self.user = username
        self.password = password
        self.name = name
        self.port = port
        self.schema = schema
        self.connection = None

    def select_all_rows(self, sql, parameters):
        cursor = self.get_cursor()
        cursor.execute(sql.format(self.schema), parameters)
        results = cursor.fetchall()
        cursor.close()
        return results

    def select_all_no_params(self, sql):
        cursor = self.get_cursor()
        cursor.execute(sql.format(self.schema))
        results = cursor.fetchall()
        cursor.close()
        return results

    def execute_cmd(self, sql, paramters):
        with self.get_cursor() as cursor:
            cursor.execute(sql.format(self.schema), paramters)
            self.connection.commit()

    def select_first_row(self, sql, parameters):
        cursor = self.get_cursor()
        cursor.execute(sql.format(self.schema), parameters)
        result = cursor.fetchone()
        cursor.close()
        return result

    def get_cursor(self):
        if not self.connection:
            self.connection = psycopg2.connect(host=self.host, user=self.user, password=self.password,
                                               dbname=self.name, port=self.port)
        return self.connection.cursor(cursor_factory=RealDictCursor)