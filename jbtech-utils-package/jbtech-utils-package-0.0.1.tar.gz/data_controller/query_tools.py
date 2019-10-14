"""A place for quick tools that can be used to help querying"""

def update_string_from_dict(update_dict):
    update_arr = []
    update_str = None
    for column in update_dict:
        update_arr.append(str(column) + "= '" + update_dict[column] + "'")
    for update in update_arr:
        if update_str is None:
            update_str = update
        else:
            update_str = ','.join([update_str, update])
    return update_str

def insert_string_from_dict(insert_dict):
    column_str = None
    value_str = None
    for column in insert_dict:
        if column_str is None and value_str is None:
            if type(insert_dict[column]) is str:
                value_str = "'%s'" % insert_dict[column]
            else:
                value_str = str(insert_dict[column])
            column_str = str(column)
            continue
        if (column_str is None and value_str is not None) or (column_str is not None and value_str is None):
            raise Exception("Invalid dictionary passed")
        else:
            column_str = ','.join([column_str, column])
            if type(insert_dict[column]) is str:
                value = "'%s'" % insert_dict[column]
                value_str = ','.join([value_str, value])
            else:
                value_str = ','.join([value_str, str(insert_dict[column])])

    return column_str, value_str