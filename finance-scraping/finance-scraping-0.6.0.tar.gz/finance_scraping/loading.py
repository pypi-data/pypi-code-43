import logging
import sys

import psycopg2


def get_connection(parameters):
    """
    Connect to a database.

    :param dict parameters: dictionary of connection parameters
                            where the keys are: database, db_user,
                            password, host and port
    :return: database connection
    """
    engine = psycopg2.connect(
        database=parameters['database'],
        user=parameters['db_user'],
        password=parameters['password'],
        host=parameters['host'],
        port=parameters['port'],
    )
    return engine


def table_exists(table_name, connection, database_engine='postgres'):
    """
    Check if the table exists in the database.

    :param str table_name: name of the table
    :param connection: psycopg2 connection object
    :param str database_engine: optional, default 'postgres'
    :return bool: True if the table exists, else False
    """
    cur = connection.cursor()

    if database_engine == 'postgres':
        query = """
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_name = %s
            );"""
        cur.execute(query, (table_name,))
        return cur.fetchone()[0]


def execute_sqls(statements, connection):
    """
    Execute a list of SQL statements.

    Statements should be passed this way:
    [("SELECT * FROM friends WHERE age > %s", (42,)), ...]

    :param list statements: a list of SQL statements and associated query
                            parameters
    :param connection: a psycopg2 connection object
    """
    cur = connection.cursor()
    try:
        for s in statements:
            cur.execute(*s)
    except Exception as e:
        logging.critical(e)
        connection.rollback()
        raise
    finally:
        connection.commit()
        connection.close()


def execute_sql_file(file_name, connection):
    with open(file_name) as f:
        sqls = tuple(
            s.strip() + ';' for s in f.read().split(';') if s != '\n'
        )
    statements = []
    for s in sqls:
        statements.append((s, ()))
    execute_sqls(statements, connection)


def data_already_loaded(table_name, collection_date, connection):
    """
    Determines if data corresponding to the collection date was already
    loaded in the database.

    :param str table_name: name of the table
    :param str collection_date: date of web scraping
    :param connection: psycopg2 connection object
    :return bool: True if rows having the specified collection date are
                  present in the database
    """
    statement = f"""
        SELECT EXISTS (
            SELECT 1 FROM {table_name}
            WHERE collection_date = %s
        );"""
    cur = connection.cursor()
    cur.execute(statement, (collection_date,))
    return cur.fetchone()[0]


def check_table_for_loaded_data(
    table_name,
    collection_date,
    connection,
    delete_if_found=False
):
    """
    Check the table for already loaded data corresponding to the collection
    date.

    :param str table_name: name of the table to check
    :param str collection_date: date when data is collected
    :param connection: psycopg2 connection object
    :param bool delete_if_found: delete already loaded data if it is found
    """
    if data_already_loaded(table_name, collection_date, connection):
        msg = f"data was already loaded on {collection_date}"
        logging.info(msg)

        if delete_if_found:
            msg = f"deleting already loaded data from table '{table_name}'"
            logging.info(msg)
            delete_statement = "DELETE FROM %s WHERE collection_date = %s;"
            execute_sqls(
                [(delete_statement, (table_name, collection_date))],
                connection
            )

        else:
            msg = f"aborting load in table '{table_name}'"
            logging.info(msg)
            sys.exit()


def copy_into(
    file_object,
    table_name,
    connection,
    separator=',',
    null_if='NULL'
):
    """
    Copy a file-like object into the specified table.

    :param str file_object: should have read() and readline() methods
    :param str table_name: name of the table to load data into
    :param connection: psycopg2 connection object
    :param str separator: field separator of the file, optional (default ',')
    :param str null_if: textual representation of NULL values in the file,
                        optional (default 'NULL')
    """
    cur = connection.cursor()
    try:
        cur.copy_from(
            file=file_object,
            table=table_name,
            sep=separator,
            null=null_if
        )
    except Exception as e:
        logging.critical(e)
        connection.rollback()
        raise
    finally:
        connection.commit()
        connection.close()
