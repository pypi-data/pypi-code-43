import pandas as pd

from mapy.utils.utils import get_min_max_from_value_range, \
    is_none
from mapy.utils.utils import is_iterable
from functools import wraps


def single_column_wrapper(func):
    @wraps(func)
    def validator(data: pd.DataFrame, column: str, **kwargs):
        assert column in data.columns, f'Base column {column} not in the data'

        validate = func(**kwargs)

        validateAnswer = data[column].apply(lambda x: validate(x))
        validateAnswer.name = f'{column}__{func.__name__}'

        return validateAnswer

    return validator


@single_column_wrapper
def value_in_range(valueRange: tuple, allowNull=False):
    """
    Asserts the the value given is in the range.
    :param allowNull: should raise exception for NA
    """

    minInRange, maxInRange = get_min_max_from_value_range(valueRange)

    def validate(x):
        if is_none(x):

            if not allowNull:
                return False

            return True

        return (x <= maxInRange) & (x >= minInRange)

    return validate


@single_column_wrapper
def validate_value_length(desiredValueLengths: set, allowNull=False):
    """
    Asserts that the length of the value is the same as desiredValueLength.
    :param allowNull: should raise exception for NA
    :param desiredValueLengths: set of possible value lengths
    """

    def validate(x):
        VALID_TYPES = (str, list, set, dict)
        if not isinstance(x, VALID_TYPES):

            if is_none(x):

                if not allowNull:
                    return False

                return True

            return False

        currentValueLength = len(x)

        return (currentValueLength in desiredValueLengths)

    return validate


@single_column_wrapper
def value_in_set(setOfValues: set, allowNull=False):
    """
    Asserts that the value is the in the set of all posible values given by setOfValues.
    :param allowNull: should raise exception for NA
    """

    assert not pd.isna(setOfValues), f'setOfValues needs to have at least one option: got {setOfValues}'
    assert is_iterable(setOfValues), f'setOfValues most be iterable: got {type(setOfValues)}'

    def validate(x):
        if is_none(x):

            if not allowNull:
                return False

            return True

        return x in set(setOfValues)

    return validate


@single_column_wrapper
def all_keys_in_set(setOfKeys: set, allowEmptyDict=False, allowNull=False):
    """
    Asserts that all keys are in the set specified
    :param setOfKeys: the set in which all keys most be contained
    :param allowEmptyDict: whether or not to allow empty dictionaries.
           if True all columns should be empty for the test to pass.
           if False an empty dict will cause the test to fail
    """
    assert is_iterable(setOfKeys), f'columns must be iterable: got {type(setOfKeys)}'

    def validate(x):

        if not isinstance(x, dict):

            if is_none(x):

                if not allowNull:
                    return False

                return True

            return False

        if (len(x) == 0) and not allowEmptyDict:
            return False

        keysNotInSet = set(x.keys()) - set(setOfKeys)

        return not keysNotInSet

    return validate


@single_column_wrapper
def sum_of_values_in_range(valueRange, allowEmptyDict=False, allowNull=False):
    """
    Asserts that the sum of values is in the specified range
    :param valueRange: the range in which most be the sum of values
    :param allowEmptyDict: whether or not to allow empty dictionaries.
           if True all columns should be empty for the test to pass.
           if False an empty dict will cause the test to fail
    """

    minInRange, maxInRange = get_min_max_from_value_range(valueRange)

    def validate(x):
        if is_none(x):

            if not allowNull:
                return False

            return True

        if (len(x) == 0) and allowEmptyDict:
            return True

        sumOfValues = sum(x.values())
        return (sumOfValues >= minInRange) and (sumOfValues <= maxInRange)

    return validate


@single_column_wrapper
def all_lower_case(allowNull=False):
    """
    Asserts that value is lower case
    :param allowNull: should raise exception for NA
    """

    def validate(x):
        if is_none(x):

            if not allowNull:
                return False

            return True

        return x.lower() == x

    return validate


@single_column_wrapper
def all_upper_case(allowNull=False):
    """
    Asserts that value is upper case
    :param allowNull: should raise exception for NA
    """

    def validate(x):
        if is_none(x):

            if not allowNull:
                return False

            return True

        return x.upper() == x

    return validate


@single_column_wrapper
def not_empty(allowNull=False):
    """
    Asserts that value is an iterable and is not empty
    :param allowNull: should raise exception for NA
    """

    def validate(x):
        ITER_TYPES = (tuple, list, set, dict)

        if not isinstance(x, ITER_TYPES) or (is_none(x) and not allowNull):
            return False

        return len(x) > 0

    return validate


@single_column_wrapper
def not_null():
    """
    Asserts that value is not null
    """

    def validate(x):
        ITER_TYPES = (tuple, list, set, dict)

        if isinstance(x, ITER_TYPES):
            return False

        return not is_none(x)

    return validate
