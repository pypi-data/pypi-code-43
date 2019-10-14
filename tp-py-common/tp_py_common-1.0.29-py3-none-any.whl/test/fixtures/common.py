import pytest
import os

from tp.test.utils import load_config
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
# from models.Base import init_db, db_session, engine as db_engine
from contextlib import contextmanager
from models import Patient, Customer, Admin

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
    db_config = load_config()
    credentials = db_config['Database']['connection']

    username = credentials['user']
    password = credentials['password']
    host = credentials['host']
    port = '3306'
    database = 'Pharmacy_Test'

    engine = create_engine('mysql://%s:%s@%s:%s' % (username, password, host, port))

    with engine.connect() as conn:
        conn.execute('commit')
        conn.execute(f'CREATE DATABASE {database}')

    yield engine

    print(f'Deleting test database {database}')

    with engine.connect() as conn:
        conn.execute('rollback')
        conn.execute(f'DROP DATABASE {database}')

# @pytest.fixture(name="db_objects", scope="session")
# def db_objects_(test_database):
    # Session = sessionmaker(bind=engine)
    # db_session = scoped_session(Session)

    # Base = declarative_base()

    # Base.query = db_session.query_property()
#     init_db()



@pytest.fixture(name="db_session")
def db_session_(test_database):
    """Session fixture that uses a non-ORM transaction to roll back.

    This is the strategy recommended in the SQLAlchemy docs. See
    http://bit.ly/1Q6Dv3p.
    """
    import models
    Session = sessionmaker(bind=test_database)
    db_session = scoped_session(Session)

    Base = declarative_base()

    Base.query = db_session.query_property()
    Base.metadata.create_all(bind=test_database)

    with non_orm_transaction(test_database) as connection:
        db_session.remove()
        db_session(bind=connection)
        connection.execute('USE Pharmacy_Test')
        for file in os.listdir('db/seeds_test'):
            for line in open(file):
                connection.execute(line)
        # Start a nested transaction (SAVEPOINT) in case the test does a
        # ROLLBACK. This gets cleaned up when the connection is closed even if
        # the test doesn't ROLLBACK.
        print('> Begin nested')
        db_session.begin_nested()
        yield db_session

@pytest.fixture(autouse=True)
def admin_user(db_session):
    try:
        admin_user = db_session.query(Admin).one()
        assert db_session.query(Admin).count() == 1
        return admin_user
    except Exception as e:
        print(f'Fixture not loaded {e}')

@pytest.fixture(autouse=True)
def customer(db_session):
    try:
        customer = db_session.query(Customer).first()
        assert db_session.query(Customer).count() == 2
        return customer
    except Exception as e:
        print(f'Fixture not loaded {e}')


@pytest.fixture(autouse=True)
def patient(db_session, customer):
    try:
        patient = db_session.query(Patient).first()
        patient.customer_id = customer.id
        db_session.commit()
        assert db_session.query(Patient).count() == 2
        return patient
    except Exception as e:
        print(f'Fixture not loaded {e}')

