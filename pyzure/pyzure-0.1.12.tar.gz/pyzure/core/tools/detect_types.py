import datetime


def detect_type(name, example):
    print('Define type of %s...' % name)
    try:
        datetime.datetime.strptime(example[:10], "%Y-%m-%d")
        return "DATETIME"
    except:
        pass
    if isinstance(example, str):
        if len(example) >= 255:
            return "TEXT"
    elif isinstance(example, bool):
        return "BIT"
    elif isinstance(example, int):
        if example > 2147483646:
            return "BIGINT"
        else:
            return "INTEGER"
    elif isinstance(example, float):
        return "FLOAT"
    try:
        float(example)
        if '.' in example:
            return "FLOAT"
        if len(example) < 11:
            return "INTEGER"
        return "VARCHAR(256)"
    except ValueError:
        return "VARCHAR(256)"

# Could be challenged by:
# def detect_type(_dbstream, name, example):
#     print('Define type of %s...' % name)
#     try:
#         query = "SELECT CAST('%s' as DATETIME)" % example
#         _dbstream.execute_query(query)
#         return "DATETIME"
#     except pyodbc.Error:
#         pass
#     if type(example) == str:
#         if len(example) >= 255:
#             return "TEXT"
#         return "VARCHAR(255)"
#     elif type(example) == int:
#         if example > 2147483646:
#             return "BIGINT"
#         else:
#             return "INTEGER"
#     elif type(example) == float:
#         return "FLOAT"
#     else:
#         return "VARCHAR(256)"
def find_sample_value(df, name, i):
    if df[name].dtype == 'object':
        df[name] = df[name].apply(lambda x: str(x) if x is not None else '')
        return df[name][df[name].map(len) == df[name].map(len).max()].iloc[0]
    else:
        rows = df.values.tolist()
        for row in rows:
            value = row[i]
            if value is not None:
                return value
        return None