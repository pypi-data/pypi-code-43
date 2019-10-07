import pandas as pd
from functools import wraps

from mapy.utils.utils import validate_columns_in_the_data, is_number


def multiple_columns_wrapper(func):
    @wraps(func)
    def validator(*args, **kwargs):
        columnOne = kwargs['columnOne']
        columnTwo = kwargs['columnTwo']
        data = kwargs['data']

        assert columnOne != columnTwo, f'Columns must be different. got {columnOne}'
        validate_columns_in_the_data(data=data, columns=[columnOne, columnTwo])

        validateFunction = func(*args, **kwargs)
        validateAnswer = data.apply(lambda row: validateFunction(row), 1)
        validateAnswer.name = f'{columnOne}_{columnTwo}__{func.__name__}'

        return validateAnswer

    return validator


@multiple_columns_wrapper
def value_greater_than_other_column(columnOne, columnTwo, data, allowNull=False):
    """
    Asserts that the value in columnOne is greater then the value in columnTwo
    :param allowNull: Will return False if one of the values is null
    """

    def validate(row):
        firstValue = row[columnOne]
        secondValue = row[columnTwo]

        if pd.isna(firstValue) or pd.isna(secondValue):
            return allowNull and pd.isna(firstValue) and pd.isna(secondValue)

        if not all(is_number(value) for value in [firstValue, secondValue]):
            return False

        return firstValue > secondValue

    return validate


@multiple_columns_wrapper
def value_greater_equal_than_other_column(columnOne, columnTwo, data, allowNull=False):
    """
    Asserts that the value in columnOne is greater or equal the value in columnTwo
    :param allowNull: Will return False if one of the values is null
    """

    def validate(row):
        firstValue = row[columnOne]
        secondValue = row[columnTwo]

        if pd.isna(firstValue) or pd.isna(secondValue):
            return allowNull and pd.isna(firstValue) and pd.isna(secondValue)

        if not all(isinstance(value, (int, float)) for value in [firstValue, secondValue]):
            return False

        return firstValue >= secondValue

    return validate


@multiple_columns_wrapper
def value_greater_than_other_column_by_n(columnOne, columnTwo, data, n, allowNull=False):
    """
    Asserts that the value in columnOne is at least greater then the value in columnTwo by a constant n
    :param allowNull: Will return False if one of the values is null
    """

    def validate(row):
        firstValue = row[columnOne]
        secondValue = row[columnTwo]

        if pd.isna(firstValue) or pd.isna(secondValue):
            return allowNull and pd.isna(firstValue) and pd.isna(secondValue)

        if not all(isinstance(value, (int, float)) for value in [firstValue, secondValue, n]):
            return False

        return firstValue > (secondValue + n)

    return validate


@multiple_columns_wrapper
def value_greater_equal_than_other_column_by_n(columnOne, columnTwo, data, n, allowNull=False):
    """
    Asserts that the value in columnOne is at least equal the value in columnTwo by a constant n
    :param allowNull: Will return False if one of the values is null
    """

    def validate(row):
        firstValue = row[columnOne]
        secondValue = row[columnTwo]

        if pd.isna(firstValue) or pd.isna(secondValue):
            return allowNull and pd.isna(firstValue) and pd.isna(secondValue)

        if not all(isinstance(value, (int, float)) for value in [firstValue, secondValue, n]):
            return False

        return firstValue >= (secondValue + n)

    return validate


@multiple_columns_wrapper
def value_less_than_other_column(columnOne, columnTwo, data, allowNull=False):
    """
    Asserts that the value in columnOne is less then the value in columnTwo
    :param allowNull: Will return False if one of the values is null
    """

    def validate(row):
        firstValue = row[columnOne]
        secondValue = row[columnTwo]

        if pd.isna(firstValue) or pd.isna(secondValue):
            return allowNull and pd.isna(firstValue) and pd.isna(secondValue)

        if not all(isinstance(value, (int, float)) for value in [firstValue, secondValue]):
            return False

        return firstValue < secondValue

    return validate


@multiple_columns_wrapper
def value_less_equal_than_other_column(columnOne, columnTwo, data, allowNull=False):
    """
    Asserts that the value in columnOne is less or equal the value in columnTwo
    :param allowNull: Will return False if one of the values is null
    """

    def validate(row):
        firstValue = row[columnOne]
        secondValue = row[columnTwo]

        if pd.isna(firstValue) or pd.isna(secondValue):
            return allowNull and pd.isna(firstValue) and pd.isna(secondValue)

        if not all(isinstance(value, (int, float)) for value in [firstValue, secondValue]):
            return False

        return firstValue <= secondValue

    return validate


@multiple_columns_wrapper
def keys_identical_to_other_column(columnOne, columnTwo, data, allowNull=False):
    """
    Asserts that the keys in columnOne are identical to the keys in columnTwo
    :param allowNull: Will return False if one of the values is null
    """

    def validate(row):
        firstValue = row[columnOne]
        secondValue = row[columnTwo]

        if pd.isna(firstValue) or pd.isna(secondValue):
            return allowNull and pd.isna(firstValue) and pd.isna(secondValue)

        if not all(isinstance(value, dict) for value in [firstValue, secondValue]):
            return False

        return len(set(firstValue) ^ set(secondValue)) == 0

    return validate


@multiple_columns_wrapper
def keys_subset_of_other_column(columnOne, columnTwo, data, allowNull=False):
    """
    Asserts that the keys in columnOne are a subset of the keys in columnTwo
    :param allowNull: Will return False if one of the values is null
    """

    def validate(row):
        firstValue = row[columnOne]
        secondValue = row[columnTwo]

        if pd.isna(firstValue) or pd.isna(secondValue):
            return allowNull and pd.isna(firstValue) and pd.isna(secondValue)

        if not all(isinstance(value, dict) for value in [firstValue, secondValue]):
            return False

        return len(set(firstValue.keys()) - set(secondValue.keys())) == 0

    return validate


@multiple_columns_wrapper
def keys_substring_of_other_column(columnOne, columnTwo, data, allowNull=False):
    """
    Asserts that every key in columnOne is a substring of some key in columnTwo
    :param allowNull: Will return False if one of the values is null
    """

    def validate(row):
        firstValue = row[columnOne]
        secondValue = row[columnTwo]

        if pd.isna(firstValue) or pd.isna(secondValue):
            return allowNull and pd.isna(firstValue) and pd.isna(secondValue)

        if not all(isinstance(value, dict) for value in [firstValue, secondValue]):
            return False

        for keyOne in firstValue.keys():
            if not any((keyOne in keyTwo) for keyTwo in secondValue.keys()):
                return False

        return True

    return validate
