# -*- tab-width: 4; encoding: utf-8; -*-
# ex: set tabstop=4 expandtab:
# Copyright (c) 2016-2018 by Lars Klitzke, Lars.Klitzke@hs-emden-leer.de.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
import argparse
from contextlib import contextmanager
from functools import wraps

import numpy as np
from pymysql.converters import escape_float, escape_int, escape_bool
from sqlalchemy import create_engine, event
from sqlalchemy.engine.base import Engine as SQLAlchemyEngine
# A global database factory
from sqlalchemy.exc import InternalError, ProgrammingError
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.orm.session import Session
from sqlalchemy_utils import create_database

from fasvaorm.models import *
from fasvaorm.signal import *

SessionFactory = None

# The global database SQLAlchemy engine
Engine = None

# The additional parameter of the engine
ENGINE_CONFIG = None


class EngineNotInitializedError(RuntimeError):
    pass


def cleanup():
    """
    Remove all references.
    """
    global SessionFactory, Engine

    SessionFactory = None
    Engine = None


def get_session_factory():
    """
    Get the current active session factory

    Returns:
        scoped_session: The session factory
    """

    global SessionFactory

    # verify that the session is initialized
    if not SessionFactory:
        # otherwise setup the session factory
        SessionFactory = init_session_factory()

    return SessionFactory


def get_engine():
    """
    Get the current active engine

    Returns:
        SQLAlchemyEngine: The current engine
    """
    global Engine
    return Engine


def add_numpy_converter(connection, *args, **kwargs):
    """
    Add numpy type converter to the connection
    """

    # floating point values
    connection.connection.connection.encoders[np.float64] = escape_float
    connection.connection.connection.encoders[np.float32] = escape_float
    connection.connection.connection.encoders[np.float16] = escape_float
    connection.connection.connection.encoders[np.double] = escape_float

    # integers
    connection.connection.connection.encoders[np.int64] = escape_int
    connection.connection.connection.encoders[np.int32] = escape_int
    connection.connection.connection.encoders[np.int16] = escape_int
    connection.connection.connection.encoders[np.int8] = escape_int

    # bool
    connection.connection.connection.encoders[np.bool8] = escape_bool


def initialize_engine(engine):
    """
    Initialize the database of the given engine
    Args:
        engine (SQLAlchemyEngine): The engine to initialize

    """

    try:
        # try to create the database
        create_database(str(engine.url))
    except ProgrammingError:
        # the database already exists
        pass

    # create all tables
    Base.metadata.create_all(engine)


def set_engine(engine):
    """
    Set the current active engine

    Args:
        engine (SQLAlchemyEngine): The new global engine
    """

    global Engine
    Engine = engine

    if Engine is not None:
        # setup bindings and create tables
        Base.metadata.bind = Engine

        try:
            Base.metadata.create_all(Engine)
        except InternalError as e:
            if 'Unknown database' in e.orig.args[1]:
                initialize_engine(Engine)

        # update the tables
        Base.metadata.reflect(Engine)


def init_engine(url, **kwargs):
    """
    Initialize the global SQLAlchemy database engine

    Args:
        url (str):  URL to connect with
        **kwargs:   Arguments passed to the `create_engine()` function.

    Returns:
        SQLAlchemyEngine: The global engine
    """

    engine = get_engine()

    # only init the global engine once
    if not engine:
        global ENGINE_CONFIG

        default_config = {
            # size of connection pool
            'pool_size': 0,
            # number of seconds until a connection timeout arise
            'pool_timeout': 10,
            # pre ping feature
            'pool_pre_ping': True,
            # recycle connection after the number of seconds without activity
            'pool_recycle': 3600
        }

        for option, value in default_config.items():
            if option not in kwargs:
                kwargs[option] = value

        ENGINE_CONFIG = kwargs

        engine = create_engine(url, **kwargs)

        event.listen(engine, "before_cursor_execute", add_numpy_converter)

    set_engine(engine)

    return engine


def init_session_factory(engine=None):
    """
    Initialize the global database session factory

    Args:
        engine (SQLAlchemyEngine): The SQLALchemy engine

    Returns:
        scoped_session: The session factory to create sessions with

    Raises:
        EngineNotInitializedError: If the passed engine (if defined) or the global engine is not initialized.
    """

    if not engine:
        engine = get_engine()

    if not engine:
        raise EngineNotInitializedError('Either pass a engine to use or initialize the global engine.')

    global SessionFactory

    # only init the global session factory once
    if not SessionFactory:
        # SessionFactory = scoped_session(sessionmaker(bind=engine))
        SessionFactory = sessionmaker(bind=engine)

    return SessionFactory


@contextmanager
def session():
    """
    Initialize a SQLAlchemy database session

    Yields:
        Session: A database session
    """
    factory = get_session_factory()
    session = factory()
    try:
        yield session
    finally:
        session.close()


def close_session(session=None):
    """
    Close the session of the current scope.

    Args:
        session (Session): The session to close.
    """
    if session:
        session.close()
    else:
        get_session_factory().remove()


def init_session():
    """
    Initialize a SQLAlchemy database session

    Returns:
        Session: A database session
    """
    return get_session_factory()()


get_session = init_session


def reload_tables():
    """
    Reload the tables of the current engine

    Notes:
        You may call this function if you've created new tables while the engine is connected.

    """
    Base.metadata.reflect()


def isolate(func):
    """
    Run the given func in an isolated environment with its own engine

    Args:
        func (callable): The function to run

        *args:
        **kwargs:

    Returns:
        func: The isolated function
    """

    @wraps(func)
    def _isolate(*args, **kwargs):
        # dispose the connections in the internal pool of the engine
        engine = get_engine()
        engine.dispose()

        # run the user function
        return func(*args, **kwargs)

    return _isolate


def parse_arguments():  # pragma: no cover
    """ Parses the arguments the user passed to this script """

    arg_parser = argparse.ArgumentParser(description="""Initialize a database.""")

    arg_parser.add_argument('--config', help="""
        Configuration file for database configuration and enrichment parametrisation""", required=False)

    arg_parser.add_argument('--log-level', help="""
        defines which messages should be logged (INFO, DEBUG, WARNING, ERROR).
        For further modes see the logging class.
        """, default='INFO', choices=['INFO', 'DEBUG', 'WARNING', 'ERROR'])

    return arg_parser.parse_args()


def initialize_database():  # pragma: no cover
    """
    Initialize a database using parameters defined as program arguments
    """

    import os
    import sys
    import pymodconf as mc

    # Section for the information about the database
    database = "Database"

    mapping = {
        database: [
            "host",
            "port",
            "user",
            "password",
        ]
    }

    arguments = parse_arguments()

    config_file_name = arguments.config

    # load the configuration
    if not config_file_name:
        # we assume that the configuration file is in our
        config_file_name = os.path.join(sys.prefix, 'share', 'fasva', 'fasva.cfg')

    config = mc.parser.load(config_file_name, mapping)

    url = "mysql+pymysql://{user}:{password}@{host}:{port}/{database}".format(**config[database])

    init_engine(url)


if __name__ == '__main__':  # pragma: no cover
    initialize_database()
