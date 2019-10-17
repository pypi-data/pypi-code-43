from pyzure.core.Table import get_table_info
from pyzure.core.tools.detect_types import detect_type, find_sample_value
import pandas as pd


def create_columns(_dbstream, data, other_table_to_update):
    table_name = data["table_name"]
    rows = data["rows"]
    columns_name = data["columns_name"]
    infos = get_table_info(_dbstream=_dbstream, table_and_schema_name=table_name)
    all_column_in_table = [e['column_name'] for e in infos]
    df = pd.DataFrame(rows, columns=columns_name)
    queries = []
    for column_name in columns_name:
        if column_name not in all_column_in_table:
            example = find_sample_value(df, column_name, columns_name.index(column_name))
            type_ = detect_type(name=column_name, example=example)
            query = """
            alter table %s
            add "%s" %s
            default NULL
            """ % (table_name, column_name, type_)
            queries.append(query)
            if other_table_to_update:
                query = """
                alter table %s
                add "%s" %s
                default NULL
                """ % (other_table_to_update, column_name, type_)
                queries.append(query)
    if queries:
        query = ' '.join(queries)
        print(query)
        _dbstream.execute_query(query)
    return 0


def extend_column(_dbstream, data, other_table_to_update=None):
    table_name = data["table_name"]
    rows = data["rows"]
    columns_name = data["columns_name"]
    df = pd.DataFrame(rows, columns=columns_name)
    for c in columns_name:
        example = find_sample_value(df, c, columns_name.index(c))
        if isinstance(example, str):
            if len(example) >= 255:
                type_ = "TEXT"
                query = """ALTER TABLE %(table_name)s ALTER COLUMN "%(column_name)s" %(type_)s""" % {
                    "table_name": table_name,
                    "column_name": c,
                    "type_": type_
                }
                _dbstream.execute_query(query)
                if other_table_to_update:
                    query = """ALTER TABLE %(table_name)s ALTER COLUMN "%(column_name)s" %(type_)s""" % {
                        "table_name": other_table_to_update,
                        "column_name": c,
                        "type_": type_
                    }
                    _dbstream.execute_query(query)
    return 0
