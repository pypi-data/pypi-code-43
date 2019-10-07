import pytest
from sqlalchemy import create_engine
from models.Base import load_config, engine, init_db, db_session
from contextlib import contextmanager

def terminate_database_connections(conn, database_name):
    conn.execute(
        f"""SELECT pg_terminate_backend(pg_stat_activity.pid)
       FROM pg_stat_activity
       WHERE pg_stat_activity.datname = '{database_name}'
       AND pid <> pg_backend_pid()"""
    )


@contextmanager
def non_orm_transaction(db_engine):
    """Context manager for a transaction on a database connection.

    Yields the database connection with an active transaction that is
    rolled back when the context manager exits.
    """
    connection = db_engine.connect()
    try:
        print('> Begin non-ORM transaction')
        connection.begin()
        yield connection
    finally:
        print('< Rollback non-ORM transaction')
        # Unconditionally roll back transactions/savepoints and close.
        connection.close()

@pytest.fixture(name='test_database', scope='session')
def test_database_():
    credentials = load_config()

    username = credentials["username"]
    password = credentials["password"]
    host = credentials["host"]
    port = credentials["port"]
    database = credentials["database"] + 'mysql'

    engine = create_engine('mysql://%s:%s@%s:%s/%s' % (username, password, host, port, database))

    with engine.connect() as conn:
        conn.execute('commit')
        conn.execute(f'CREATE DATABASE "{database}"')
        yield

        print(f'Deleting test database {database}')

        with engine.connect() as conn:
            conn.execute('rollback')
            terminate_database_connections(conn, database)
            conn.execute(f'DROP DATABASE "{database}"')

@pytest.fixture(name="db_objects", scope="session")
def db_objects_(test_database):
    init_db()

@pytest.fixture(name="db_session")
def db_session_(db_objects):
    """Session fixture that uses a non-ORM transaction to roll back.

    This is the strategy recommended in the SQLAlchemy docs. See
    http://bit.ly/1Q6Dv3p.
    """
    with non_orm_transaction(engine) as connection:
        db_session.remove()
        db_session(bind=connection)

         # Start a nested transaction (SAVEPOINT) in case the test does a
        # ROLLBACK. This gets cleaned up when the connection is closed even if
        # the test doesn't ROLLBACK.
        print('> Begin nested')
        db_session.begin_nested()
        yield db_session