import sqlalchemy as db
from jinjasql import JinjaSql


def in_range(table, column, args=None):
    """
    Check whether values in a column fall within a specific range.

    Args:
        min (int): the minimum value of the range
        max (int): the maximum value of the range
    """
    assert 'min' in args
    assert 'max' in args

    return db.select([table]).where(db.or_(column < args['min'],
                                           column > args['max']))


def accepted_values(table, column, args=None):
    """
    Check that a column contains only specified values.

    Args:
        vals (list): a list of values

    """
    assert 'vals' in args

    return db.select([table]).where(column.notin_(args['vals']))


def not_null(table, column, args=None):
    """
    Check that a column contains only non-`NULL` values.
    """
    return db.select([table]).where(column.is_(None))


def unique(table, column, args=None):
    """
    Check whether values in a column are unique.
    """
    return db.select([column]) \
        .select_from(table) \
        .group_by(column) \
        .having(db.func.count(column) > 1)


def custom_sql(table, column, args=None):
    """
    Execute a custom (optionally Jinja-formatted) SQL query and fail if
    non-zero number of rows is returned.

    Either ``query`` or ``query_file`` parameter needs to be provided. All the
    other arguments are passed as Jinja variables and can be used to build the
    query.

    Args:
        query (str): query to be executed (optional).
        query_file (str): path to the file in which the query to be executed
                          can be found (optional)
    """
    j = JinjaSql(param_style='pyformat')

    if 'query_file' in args:
        q_str = open(args['query_file']).read()
    if 'query' in args:
        q_str = args['query']

    args['table'] = table.name
    args['column'] = column.name

    query, bind_params = j.prepare_query(q_str, args)

    return query % bind_params
