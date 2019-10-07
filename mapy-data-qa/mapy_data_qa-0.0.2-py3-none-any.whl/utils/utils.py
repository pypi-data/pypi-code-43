import operator
from functools import wraps

from pandas.api.types import is_string_dtype
from pandas.api.types import is_numeric_dtype

from typing import List
import pandas as pd
import numpy as np


def is_number(x):
    try:
        int(x)
        return True

    except ValueError:
        return False


def validate_column_data_types(BASE_COLUMNS: List, df: pd.DataFrame) -> None:
    columnsToTypes = df.dtypes

    for column in BASE_COLUMNS:

        assert column['name'] in columnsToTypes, f'Base column {column["name"]} not in the data'

        if is_numeric_dtype(column['type']):
            assert \
                is_numeric_dtype(columnsToTypes[column['name']]), \
                f"Base column {column['name']} is of type {columnsToTypes[column['name']]} " \
                f"and should be {column['type']}"

        elif column['type'] == dict:
            assert all(isinstance(row, dict) for row in df[column['name']]), \
                f"Base column {column['name']} is of type {columnsToTypes[column['name']]} " \
                f"and should be {column['type']}"

        elif column['type'] == set:
            assert all(isinstance(row, set) for row in df[column['name']]), \
                f"Base column {column['name']} is of type {columnsToTypes[column['name']]} " \
                f"and should be {column['type']}"

        elif is_string_dtype(column['type']):
            assert is_string_dtype(columnsToTypes[column['name']]), \
                f"Base column {column['name']} is of type {columnsToTypes[column['name']]} " \
                f"and should be {column['type']}"

        else:
            raise Exception(
                f"Base column {column['name']} is not of valid type. "
                f"{columnsToTypes[column['name']]} and should be {column['type']}")


def timeit(method):
    import time

    @wraps(method)
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)

        else:
            print(f'{method.__name__}  {(te - ts) * 1000:2.2f} ms')

        return result

    return timed


def is_iterable(item):
    """
    check if some item is iterable
    :return bool: if the item is iterable
    """
    if isinstance(item, str):
        return False

    try:
        iter(item)
        return True

    except TypeError:
        return False


# TODO: rename. get_max_len_of_set_in_dict
# TODO: not tested. test also when not iterable
def get_len_of_sets_in_a_dict(iterable):
    """
    example:

    iterable = {'dong': {'a', 'b'}, 'ding': {'c'}}
    :returns max([2, 1]) => 2

    :param iterable: dict with {str: iterable} values
    :return: the length of the single longest iterable in the dict
    """
    if not iterable:
        return 0

    return max([len(item) for item in iterable.values()])


# TODO: why are they called iterable if they're dict ?
def get_mean_of_sets_in_a_dict(iterable):
    """
    example:

    iterable = {'dong': {'a', 'b'}, 'ding': {'c'}}
    :returns np.mean([2, 1]) => 1.5

    :param iterable: dict with {str: iterable} values
    :return: the mean length of all values in the dict
    """
    if not iterable:
        return 0

    return np.mean([len(item) for item in iterable.values()])


def dict_to_sorted_list_of_tuples(d: dict, sortOn: str = 'values') -> list:
    """
    takes a dictionary and returns a sorted list of ('key', 'value') tuples

    example:
    d = {'a': 2, 'b': 4, 'c': 3, 'd': 1, 'e': 0}
    dict_to_sorted_list_of_tuples(d, sortOn='values')

    :returns [('e', 0), ('d', 1), ('a', 2), ('c', 3), ('b', 4)]

    dict_to_sorted_list_of_tuples(d, sortOn='keys')
    :returns [('a', 2), ('b', 4), ('c', 3), ('d', 1), ('e', 0)]

    :param d dict: a dictionary to be sorted
    :param sortOn str: "values" or "keys"
    """
    assert sortOn in {'values', 'keys'}, f'sortOn takes "values" or "keys". got {sortOn}'
    sortIndex = 0 if sortOn == 'keys' else 1

    return sorted(d.items(), key=operator.itemgetter(sortIndex))


def get_timestamp_diff(later, sooner):
    """
    Returns the time tidderence between two time stamps. default value is -1
    """
    totalTime = later - sooner
    if (totalTime >= 0) and (not pd.isna(totalTime)):
        return totalTime

    return -1


def validate_columns_in_the_data(data, columns):
    for column in columns:
        assert hasattr(data, column), f'{column} not in the data'


def validate_empty_dict(allowEmptyDict, columns, row):
    for column in columns:
        columnValue = row[column]
        assert allowEmptyDict or (len(columnValue) > 0), f'{column} has no keys'


def get_min_max_from_value_range(valueRange):
    assert (len(valueRange) == 2) and (isinstance(valueRange, tuple)), \
        f'valueRange should be a tuple of length 2: {valueRange} given'

    minInRange, maxInRange = valueRange

    assert maxInRange >= minInRange, f'Max value should be higher than min value in the range: got: {valueRange}'

    return minInRange, maxInRange


def is_none(value):
    if pd.isna(value) or (value == 'nan'):
        return True

    return False
