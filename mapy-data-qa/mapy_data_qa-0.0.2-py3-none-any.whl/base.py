from dataclasses import dataclass
# from feature_store.constants import Columns

import pandas as pd
from mapy.utils.utils import timeit, validate_column_data_types
from mapy import multiple_columns, single_column


@dataclass
class Tests:
    assert_value_greater_equal_other_column = {
        'name': 'assert_value_greater_equal_other_column',
        'apply_with_row': True
    }
    assert_value_in_range = {
        'name': 'assert_value_in_range',
        'apply_with_row': False
    }
    assert_values_greater_equal = {
        'name': 'assert_values_greater_equal',
        'apply_with_row': True
    }
    assert_value_length = {
        'name': 'assert_value_length',
        'apply_with_row': False
    }
    assert_value_in_set = {
        'name': 'assert_value_in_set',
        'apply_with_row': False
    }
    assert_identical_keys = {
        'name': 'assert_identical_keys',
        'apply_with_row': True
    }
    assert_keys_are_subset = {
        'name': 'assert_keys_are_subset',
        'apply_with_row': True
    }
    assert_all_lower_case = {
        'name': 'assert_all_lower_case',
        'apply_with_row': False
    }
    assert_all_upper_case = {
        'name': 'assert_all_upper_case',
        'apply_with_row': False
    }
    assert_not_null = {
        'name': 'assert_not_null',
        'apply_with_row': False
    }
    assert_all_keys_in_set = {
        'name': 'assert_all_keys_in_set',
        'apply_with_row': False
    }
    assert_sum_of_values_in_range = {
        'name': 'assert_sum_of_values_in_range',
        'apply_with_row': False
    }
    assert_keys_are_substring_of_other_column = {
        'name': 'assert_keys_are_substring_of_other_column',
        'apply_with_row': True
    }
    assert_keys_contained_in_other_column = {
        'name': 'assert_keys_contained_in_other_column',
        'apply_with_row': True
    }


@timeit
def data_qa(df: pd.DataFrame, ignoredColumns, qaConfig):
    """Should be applied on a dataframe after you've added all the features you need from the feature store.
       the aim is to test the final data frame for the existence of nonsensical conditions i.e a user that was
       seen in a slot app last week but has 0 slot apps in total etc.

       Parameters
       ----------
       df : The wins data frame
       ignoredColumns set: columns to be ignored (not checked) in the qa process
       """
    for column, tests in qaConfig.items():

        if column in ignoredColumns:
            print(f'{column} is ignored in type validation')
            continue

        # Get the full column attribute from the Columns class
        columnAttribute = getattr(Columns, column)

        # Validate the column data type with the desired data type specified in the Column class
        print(f'Validating column type for {column}')
        validate_column_data_types(BASE_COLUMNS=[columnAttribute], winsDf=df)

    for column, tests in qaConfig.items():

        if column in ignoredColumns:
            print(f'{column} is ignored in testing')
            continue

        for test, kwargs in tests.items():
            print(f'Testing {test} for {column}')

            # Get the test function from the testing_functions module and create an instance
            testFunction = getattr(single_column, test, getattr(multiple_columns, test))

            # Tests that require apply on row instead of a column
            if getattr(Tests, test)['apply_with_row']:
                df.apply(lambda row: testFunction(row=row, **kwargs), 1)
                continue

            # Call the test function for each value with the args from the config
            df[column].apply(lambda value: testFunction(value=value, **kwargs))
