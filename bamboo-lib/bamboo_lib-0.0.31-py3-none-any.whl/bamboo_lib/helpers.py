import os
import re
import string
import random
import itertools
import pandas as pd

from cryptography.fernet import Fernet

from bamboo_lib.exceptions import AbsolutePathException
from bamboo_lib.connectors.models import Connector

def decrypt(encrypted_str, passcode):
    """Given a string encrypted with :meth:`bamboo_lib.helpers.encrypt` and passcode, decrypt the raw string.

    :param encrypted_str: Encrypted string
    :param passcode: Password to decrypt
    :return: Decrypted string
    """
    fernet = Fernet(passcode)
    return fernet.decrypt(encrypted_str.encode("utf-8"))


def grab_parent_dir(file_starting_point):
    """Given a string indicating a system file path, build a path to the parent directory.

    :param file_starting_point: file path string from which to compute the parent directory.
    :return: String to the absolute path of the file_starting_point parent folder
    """
    return os.path.abspath(os.path.join(file_starting_point, os.pardir))


def convert_to_absolute(file_starting_point, target_relative_path):
    """Given a file starting point  and a relative path of a file, build a absolute path.

    :param file_starting_point: file path starting point with absolute path.
    :param target_realtive_path: realtive path of the file.
    :return: String to the absolute path of the target_relative_path including file_starting_point.
    """
    if os.path.isabs(file_starting_point):
        return os.path.abspath(os.path.join(file_starting_point, target_relative_path))
    else:
        raise  AbsolutePathException('File starting point is not absolute')
       

def grab_connector(file_starting_point, cname):
    """ Given a filepath and connector name, retrieves and builds the
    connector configuration object.

    :param file_starting_point: filepath from which to base the search for the conns.yaml file.
    :param cname: name of the connector to look up
    :return: Connector object
    """
    # try local file first then fall back to global
    par_dir = os.path.abspath(os.path.join(file_starting_point, os.pardir))
    local_conn_path = os.path.join(par_dir, "conns.yaml")
    # source = local_conn_path.get(cname, global_conn_path.get(cname))
    try:
        connector = Connector.fetch(cname, open(local_conn_path))
    except ValueError:
        BAMBOO_FALLBACK_CONNS = os.environ.get("BAMBOO_FALLBACK_CONNS")
        # TODO allow env var to customize default fallback config path
        global_conn_path = os.path.expanduser(os.path.expandvars(BAMBOO_FALLBACK_CONNS))
        connector = Connector.fetch(cname, open(global_conn_path))
    return connector


def random_char(num_characters):
    """ Returns a string of num_characters random ASCII characters.

    :param num_characters: Integer representing the number of characters to appear in the output.
    :return: String
    """
    return ''.join(random.choice(string.ascii_letters) for x in range(num_characters))


def dict_product(dicts):
    """ Given a dictionary of lists, returns a list of dictionaries containing the cross-product
    of associated items.

    :param dicts: Dictionary mapping names to lists
    :return: list of dict
    """
    return (dict(zip(dicts, x)) for x in itertools.product(*dicts.values()))


def expand_path(my_path_str):
    """ Given a string path, expand and replace any matching environment variables or user references.
    return os.path.expanduser(os.path.expandvars(my_path_str))

    :param my_path_str: String representing the target path
    :return: String representing the target path with any environment variables or user references.
    """
    return os.path.expanduser(os.path.expandvars(my_path_str))

def query_to_df(connector_obj, raw_query, col_headers=None):
    """ Given a :class:`bamboo_lib.connectors.models.Connector` object, raw SQL command and a list of result column headers, returns a pandas DataFrame with the results.

    :param connector_obj: Connector object
    :param raw_query: Target SQL to execute
    :param col_headers: List of column names for query results
    :return: DataFrame with query results
    """
    with_column_names = not col_headers
    result = connector_obj.raw_query(raw_query, with_column_names=with_column_names)
    if col_headers:
        if result and len(result) > 0:
            if len(col_headers) != len(result[0]):
                raise ValueError("Length of column headers list does not match the number of query result columns!")
    else:
        data, col_headers = result
        result = data
    df = pd.DataFrame(result, columns=col_headers)
    return df

def process_uri_wildcards(raw_uri):
    """Given a URI, parse out the placeholder {{tags}} and convert them to regular expressions"""
    # This regex says match on: two left braces followed by any number of non-right brace characters
    # followed by two right braces.
    my_pattern = r"\{\{([^}]+)\}\}"
    target_pattern = r"(?P<\1>.+)"
    return re.sub(my_pattern, target_pattern, raw_uri)

def wildcard_matches(pattern, target_value):
    """Given a pattern and a target, determine if the pattern regex is found in the target."""
    matches = re.search(pattern, target_value)
    return matches.groupdict() if matches else None

def table_has_duplicates(connector_obj, full_table_name, pk_cols):
    """ Given a :class:`bamboo_lib.connectors.models.Connector` object,
    a fully qualified table path and a list of primary key columns,
    this method will run a query to determine if there are are cases where the primary key
    is duplicated.

    :param connector_obj: Connector object
    :param full_table_name: Fully qualified name of table (including schema if applicable)
    :param pk_cols: List of strings with the column names to be used as the primary keys for checking uniqueness
    :return: boolean
    """
    pk_cols = ",".join(['"{}"'.format(col) for col in pk_cols])
    dupe_check_sql = """
        SELECT {pk_cols}
        FROM {full_table_name}
        GROUP BY {pk_cols}
        HAVING COUNT(1) > 1;
    """.format(pk_cols=pk_cols, full_table_name=full_table_name)
    result = connector_obj.raw_query(dupe_check_sql)
    has_dupes = len(result) > 0 if result else False
    return has_dupes