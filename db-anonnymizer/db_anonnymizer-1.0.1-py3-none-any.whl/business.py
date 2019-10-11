from datetime import datetime

import dsnparse
import faker
from faker.providers import person, internet, bank, address, company
from mysql.connector import connect

from db_anonnymizer.dbal import MySQLDBAL


class Database:
    def __init__(self, host, name, username, password):
        self.conn = connect(
            user=username,
            password=password,
            host=host,
            database=name
        )
        self.dbname = name
        self.dbal = MySQLDBAL(conn=self.conn, dbname=name)

    @property
    def tables(self):
        tables_cursor = self.dbal.get_tables()

        return [
            Table(
                name=tablename[0],
                conn=self.conn,
                dbname=self.dbname
            ) for tablename in tables_cursor
        ]

    def __str__(self):
        return self.dbname


def escaped_value(val):
    if val is None:
        return 'NULL'

    if isinstance(val, datetime):
        return "'{}'".format(val.strftime('%Y-%m-%d %H:%M:%S'))

    if isinstance(val, str):
        if "'" in val:
            return '"{}"'.format(val)
        else:
            return "'{}'".format(val)

    return str(val)


class Table:
    def __init__(self, dbname, name, conn):
        self.name = name
        self.conn = conn
        self.db = dbname

        self.dbal = MySQLDBAL(conn=conn, dbname=dbname)

        self.fake = faker.Faker()
        self.fake.add_provider(person)
        self.fake.add_provider(internet)
        self.fake.add_provider(bank)
        self.fake.add_provider(address)
        self.fake.add_provider(company)

    @property
    def fields(self):
        fields_cursor = self.dbal.get_columns(self.name, self.db)

        return [
            Field(
                name=field[0],
                type=field[1],
                length=field[2]
            ) for field in fields_cursor
        ]

    @property
    def create_sql_statement(self):
        create_table_cursor = self.dbal.get_create_statement(self.name)

        return [
            statement for table, statement in create_table_cursor
        ][0]

    def __str__(self):
        return self.name

    def anonymize(self, config):
        cursor = self.get_all_rows()

        for row in cursor:
            row_list = list(row)
            anonymized_values = self.anonymize_row(row_list, config)
            yield self.generate_insert(anonymized_values)

    def get_all_rows(self):
        cursor = self.conn.cursor(buffered=True)
        cursor.execute('select * from {}'.format(self.name))
        return cursor

    def dump(self):
        cursor = self.get_all_rows()

        for row in cursor:
            yield self.generate_insert(row)

    def generate_insert(self, row):
        return "INSERT INTO `{}` ({}) VALUES ({});".format(
            self.name,
            ", ".join(['`{}`'.format(field.name) for field in self.fields]),
            ", ".join([escaped_value(val) for val in row])
        )

    def anonymize_row(self, row, config):
        for attr, faker in config.items():
            attr_index = self.get_field_index(attr)
            row[attr_index] = self.generate_anonymized_value(faker)

        return row

    def get_field_index(self, attr):
        return [
            field.name for field in self.fields
        ].index(attr)

    def generate_anonymized_value(self, faker_name):
        return getattr(self.fake, faker_name)()


class Field:
    def __init__(self, name, type, length):
        self.name = name
        self.type = type
        self.length = length

    def __str__(self):
        return self.name


def connect_to_db(db_url):
    parsed_url = dsnparse.parse(db_url)
    return Database(
        host=parsed_url.host,
        username=parsed_url.username,
        password=parsed_url.password,
        name=parsed_url.database
    )
