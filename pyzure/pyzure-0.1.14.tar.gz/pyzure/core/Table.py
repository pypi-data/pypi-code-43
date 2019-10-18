import pyodbc
import pandas as pd
from pyzure.core.tools.detect_types import detect_type, find_sample_value


def get_table_info(_dbstream, table_and_schema_name):
    split = table_and_schema_name.split(".")
    if len(split) == 1:
        table_name = split[0]
        schema_name = None

    elif len(split) == 2:
        table_name = split[1]
        schema_name = split[0]
    else:
        raise Exception("Invalid table or schema name")
    query = "SELECT column_name, data_type, character_maximum_length, is_nullable FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='%s'" % table_name
    if schema_name:
        query = query + " AND TABLE_SCHEMA='%s'" % schema_name
    print(query)
    return _dbstream.execute_query(query)


def create_table_from_info(_dbstream, columns, table_name):
    columns_name_string = []
    for c in columns:
        # COLUMN NAME
        c_string = c["column_name"]

        # DATA TYPE TREATMENT
        data_type = c["data_type"]
        if data_type in ("varchar"):
            data_type = data_type + "(" + str(c["character_maximum_length"]) + ")"

        c_string = c_string + " " + data_type

        # NULLABLE ?
        if c["is_nullable"] == "NO":
            c_string = c_string + " NOT NULL"

        columns_name_string.append(c_string)

    query = "CREATE TABLE %s (%s)" % (table_name, ", ".join(columns_name_string))
    print(query)
    _dbstream.execute_query(query)


def format_create_table(data):
    table_name = data["table_name"]
    columns_name = data["columns_name"]
    rows = data["rows"]
    params = {}
    df = pd.DataFrame(rows, columns=columns_name)

    for i in range(len(columns_name)):
        name = columns_name[i]
        print(name)
        example = find_sample_value(df, name, i)
        col = dict()
        col["example"] = example
        col["type"] = detect_type(name, example)
        col["encoding"] = "ENCODE ZSTD "
        params[name] = col

    query = """"""
    query = query + "CREATE TABLE " + table_name + " ("
    col = list(params.keys())
    for i in range(len(col)):
        k = col[i]
        if i == len(col) - 1:
            query = query + "\n     \"" + k + '\" ' + params[k]["type"] + ' ' + 'NULL '
        else:
            query = query + "\n     \"" + k + '\" ' + params[k]["type"] + ' ' + 'NULL ,'
    else:
        query = query[:-1]
    query = query + "\n )"
    print(query)
    return query


def create_table(_dbstream, data):
    query = format_create_table(data)

    try:
        _dbstream.execute_query(query)
    except pyodbc.ProgrammingError as e:
        e = str(e)
        print(e)
        if "schema" in e:
            _dbstream.execute_query("CREATE SCHEMA " + data['table_name'].split(".")[0])
            _dbstream.execute_query(query)
