import logging
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql.expression import Insert
from sqlalchemy.util import safe_reraise

from dq.config import Config
from dq.errors import ModelError
from dq.funcutil import safe_invoke
from dq.logging import error

logger = logging.getLogger(__name__)

engine = create_engine(
    Config.get('sql.url'),
    pool_recycle=600,
    pool_pre_ping=True,
)
if Config.get('sql.flavor') == 'mysql':
    Insert.argument_for('mysql', 'replace_insert', None)


def session_maker():
    """Generate a scoped session. In general, use the Session global variable.

    :returns Session: A new SQLAlchemy session.
    """
    return scoped_session(sessionmaker(bind=engine))


Session = session_maker()


@compiles(Insert, 'mysql')
def replace_insert(insert, compiler, **kw):
    """Allow replace into for insert command.

    This only works for MySQL. It's not standard SQL. To enable this function,
    the sql.flavor config must be set to mysql.
    """
    s = compiler.visit_insert(insert, **kw)
    if 'mysql_replace_insert' in insert.kwargs:
        s = s.replace('INSERT INTO', 'REPLACE INTO')
    return s


@contextmanager
def commit_scope(session=None):
    """Commit any database operations within this scope."""
    session = session or Session()
    try:
        yield session
        session.commit()
    except Exception:
        with safe_reraise():
            session.rollback()


def unsafe_save_to_database(model, session=None):
    """Convenient method for writing things to the database.

    If the object is a list, its elements will be written to the database one
    by one. If the object is already in the database (i.e. when we are updating
    existing records), the caller of this function is responsible of ensuring
    that the same session used when retrieving the records is passed in. If
    a different session is provided, this operation will fail. (This is
    usually not an issue for view functions, which have session consistency on
    a thread level.)

    :param object/list model: The model object(s) to save. If a list is
        provided, the elements will be added one by one. Otherwise the object
        is added as-is.
    :param Session session: The optional database session to use.
    """
    if not model:
        return
    with commit_scope(session=session) as sess:
        if isinstance(model, list):
            for m in model:
                sess.add(m)
        else:
            sess.add(model)


def save_to_database(model, session=None):
    """Write things to the database.

    This function simply calls ``unsafe_save_to_database`` under the hood, but
    wraps the error into a ``ModelError`` upon failure.

    :param object/list model: The model object(s) to save. If a list is
        provided, the elements will be added one by one. Otherwise the object
        is added as-is.
    :param Session session: The optional database session to use.
    :raises ModelError: if the save fails.
    """
    try:
        unsafe_save_to_database(model, session=session)
    except Exception as e:
        error(logger, 'Error saving to database', {
            'model': model, 'error': e,
        })
        raise ModelError(e.message if hasattr(e, 'message') else str(e))


@safe_invoke(noreturn=True)
def safe_save_to_database(model, session=None):
    """Safely write things to the database.

    This function simply calls ``unsafe_save_to_database`` under the hood, but
    returns whether the operation is successful instead of throwing an error
    upon failure.

    :param object/list model: The model object(s) to save. If a list is
        provided, the elements will be added one by one. Otherwise the object
        is added as-is.
    :param Session session: The optional database session to use.
    :returns boolean: True if the operation is successful.
    """
    unsafe_save_to_database(model, session=session)


def query_with_limit_offset(query, limit, offset):
    """Add limit and offset constraints to a SQLAlchemy query.

    :param Query query: A SQLAlchemy query.
    :param int limit: The limit to add. If None or 0, it will be skipped.
    :param int offset: The offset to add. If None or 0, it will be skipped.
    :returns Query: The updated query object.
    """
    if limit:
        query = query.limit(limit)
    if offset:
        query = query.offset(offset)
    return query
