# -*- coding: utf-8 -*-
from sqlalchemy.orm import sessionmaker
from sqlite3 import dbapi2 as sqlite
from sqlalchemy import create_engine

class SqliteSession():

    @staticmethod
    def create(config):

        # connection string
        database = config['database']
        conn_string = f'sqlite+pysqlite:///{database}'

        # create engine
        db_engine = create_engine(conn_string, module=sqlite)

        # create session
        Session = sessionmaker(bind=db_engine)
        session = Session()

        return session
