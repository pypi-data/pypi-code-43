import pandas as pd
import numpy as np
import pytest

from mapy import multiple_columns

defaultDF = pd.DataFrame({'ido': [2, 3, 4],
                          'zehori': [1, 2, 3]})


def test_value_greater_than_other_column():
    df = pd.DataFrame({'hundreds': [200, 300, 400],
                       'hundreds2': [200, 300, 400],
                       'tens': [10, 20, 30],
                       'tens_with_nones': [10, None, 30],
                       'hundreds_with_nones': [100, None, 300],
                       'not_numbers': ['a', 'b', 'c'],
                       'none': None})

    assert all(multiple_columns.value_greater_than_other_column(columnOne='hundreds',
                                                                columnTwo='tens',
                                                                data=df,
                                                                allowNull=False))

    assert not all(multiple_columns.value_greater_than_other_column(columnOne='hundreds',
                                                                    columnTwo='hundreds2',
                                                                    data=df,
                                                                    allowNull=False))

    assert not all(multiple_columns.value_greater_than_other_column(columnOne='tens',
                                                                    columnTwo='hundreds',
                                                                    data=df,
                                                                    allowNull=False))

    assert all(multiple_columns.value_greater_than_other_column(columnOne='hundreds_with_nones',
                                                                columnTwo='tens_with_nones',
                                                                data=df,
                                                                allowNull=True))

    with pytest.raises(AssertionError):
        assert all(multiple_columns.value_greater_than_other_column(columnOne='hundreds',
                                                                    columnTwo='not_numbers',
                                                                    data=df,
                                                                    allowNull=True))

    with pytest.raises(AssertionError):
        assert all(multiple_columns.value_greater_than_other_column(columnOne='hundreds',
                                                                    columnTwo='tens_with_nones',
                                                                    data=df,
                                                                    allowNull=True))

    with pytest.raises(AssertionError):
        assert all(multiple_columns.value_greater_than_other_column(columnOne='hundreds',
                                                                    columnTwo='tens_with_nones',
                                                                    data=df,
                                                                    allowNull=False))
    with pytest.raises(AssertionError):
        assert all(multiple_columns.value_greater_than_other_column(columnOne='hundreds',
                                                                    columnTwo='none',
                                                                    data=df,
                                                                    allowNull=True))

    with pytest.raises(AssertionError):
        assert all(multiple_columns.value_greater_than_other_column(columnOne='hundreds',
                                                                    columnTwo='hundreds',
                                                                    data=df,
                                                                    allowNull=False))


def test_value_greater_equal_than_other_column():
    df = pd.DataFrame({'hundreds': [100, 300, 400],
                       'tens': [100, 20, 30],
                       'tens_with_nones': [100, None, 30],
                       'hundreds_with_nones': [100, None, 300],
                       'not_numbers': ['a', 'b', 'c'],
                       'none': None})

    assert all(multiple_columns.value_greater_equal_than_other_column(columnOne='hundreds',
                                                                      columnTwo='tens',
                                                                      data=df,
                                                                      allowNull=False))

    assert not all(multiple_columns.value_greater_equal_than_other_column(columnOne='tens',
                                                                          columnTwo='hundreds',
                                                                          data=df,
                                                                          allowNull=False))

    assert all(multiple_columns.value_greater_equal_than_other_column(columnOne='hundreds_with_nones',
                                                                      columnTwo='tens_with_nones',
                                                                      data=df,
                                                                      allowNull=True))

    with pytest.raises(AssertionError):
        assert all(multiple_columns.value_greater_equal_than_other_column(columnOne='hundreds',
                                                                          columnTwo='not_numbers',
                                                                          data=df,
                                                                          allowNull=True))

    with pytest.raises(AssertionError):
        assert all(multiple_columns.value_greater_equal_than_other_column(columnOne='hundreds',
                                                                          columnTwo='tens_with_nones',
                                                                          data=df,
                                                                          allowNull=True))

    with pytest.raises(AssertionError):
        assert all(multiple_columns.value_greater_equal_than_other_column(columnOne='hundreds',
                                                                          columnTwo='tens_with_nones',
                                                                          data=df,
                                                                          allowNull=False))
    with pytest.raises(AssertionError):
        assert all(multiple_columns.value_greater_equal_than_other_column(columnOne='hundreds',
                                                                          columnTwo='none',
                                                                          data=df,
                                                                          allowNull=True))


def test_value_greater_than_other_column_by_n():
    df = pd.DataFrame({'hundreds': [100, 300, 400],
                       'tens': [10, 20, 30],
                       'tens_with_nones': [10, None, 30],
                       'hundreds_with_nones': [100, None, 300],
                       'not_numbers': ['a', 'b', 'c'],
                       'none': None})

    assert all(multiple_columns.value_greater_than_other_column_by_n(columnOne='hundreds',
                                                                     columnTwo='tens',
                                                                     data=df,
                                                                     n=50,
                                                                     allowNull=False))

    assert not all(multiple_columns.value_greater_than_other_column_by_n(columnOne='hundreds',
                                                                         columnTwo='tens',
                                                                         data=df,
                                                                         n=500,
                                                                         allowNull=False))

    assert not all(multiple_columns.value_greater_than_other_column_by_n(columnOne='tens',
                                                                         columnTwo='hundreds',
                                                                         data=df,
                                                                         n=50,
                                                                         allowNull=False))

    assert all(multiple_columns.value_greater_than_other_column_by_n(columnOne='hundreds_with_nones',
                                                                     columnTwo='tens_with_nones',
                                                                     data=df,
                                                                     n=50,
                                                                     allowNull=True))

    with pytest.raises(AssertionError):
        assert all(multiple_columns.value_greater_than_other_column_by_n(columnOne='hundreds',
                                                                         columnTwo='not_numbers',
                                                                         data=df,
                                                                         n=10,
                                                                         allowNull=True))

    with pytest.raises(AssertionError):
        assert all(multiple_columns.value_greater_than_other_column_by_n(columnOne='hundreds',
                                                                         columnTwo='tens_with_nones',
                                                                         data=df,
                                                                         n=10,
                                                                         allowNull=True))

    with pytest.raises(AssertionError):
        assert all(multiple_columns.value_greater_than_other_column_by_n(columnOne='hundreds',
                                                                         columnTwo='tens_with_nones',
                                                                         data=df,
                                                                         n=10,
                                                                         allowNull=False))

    with pytest.raises(AssertionError):
        assert all(multiple_columns.value_greater_than_other_column_by_n(columnOne='hundreds',
                                                                         columnTwo='none',
                                                                         data=df,
                                                                         n=10,
                                                                         allowNull=True))

    with pytest.raises(AssertionError):
        assert all(multiple_columns.value_greater_than_other_column_by_n(columnOne='hundreds',
                                                                         columnTwo='tens',
                                                                         data=df,
                                                                         n=None,
                                                                         allowNull=True))

    with pytest.raises(AssertionError):
        assert all(multiple_columns.value_greater_than_other_column_by_n(columnOne='hundreds',
                                                                         columnTwo='tens',
                                                                         data=df,
                                                                         n='a',
                                                                         allowNull=True))


def test_value_greater_equal_than_other_column_by_n():
    df = pd.DataFrame({'hundreds': [100, 300, 400],
                       'tens': [10, 20, 30],
                       'tens_with_nones': [10, None, 30],
                       'hundreds_with_nones': [100, None, 300],
                       'not_numbers': ['a', 'b', 'c'],
                       'none': None})

    assert all(multiple_columns.value_greater_equal_than_other_column_by_n(columnOne='hundreds',
                                                                           columnTwo='tens',
                                                                           data=df,
                                                                           n=90,
                                                                           allowNull=False))

    assert not all(multiple_columns.value_greater_equal_than_other_column_by_n(columnOne='hundreds',
                                                                               columnTwo='tens',
                                                                               data=df,
                                                                               n=500,
                                                                               allowNull=False))

    assert not all(multiple_columns.value_greater_equal_than_other_column_by_n(columnOne='tens',
                                                                               columnTwo='hundreds',
                                                                               data=df,
                                                                               n=50,
                                                                               allowNull=False))

    assert all(multiple_columns.value_greater_equal_than_other_column_by_n(columnOne='hundreds_with_nones',
                                                                           columnTwo='tens_with_nones',
                                                                           data=df,
                                                                           n=90,
                                                                           allowNull=True))

    with pytest.raises(AssertionError):
        assert all(multiple_columns.value_greater_equal_than_other_column_by_n(columnOne='hundreds',
                                                                               columnTwo='not_numbers',
                                                                               data=df,
                                                                               n=10,
                                                                               allowNull=True))

    with pytest.raises(AssertionError):
        assert all(multiple_columns.value_greater_equal_than_other_column_by_n(columnOne='hundreds',
                                                                               columnTwo='tens_with_nones',
                                                                               data=df,
                                                                               n=10,
                                                                               allowNull=True))

    with pytest.raises(AssertionError):
        assert all(multiple_columns.value_greater_equal_than_other_column_by_n(columnOne='hundreds',
                                                                               columnTwo='tens_with_nones',
                                                                               data=df,
                                                                               n=10,
                                                                               allowNull=False))

    with pytest.raises(AssertionError):
        assert all(multiple_columns.value_greater_equal_than_other_column_by_n(columnOne='hundreds',
                                                                               columnTwo='none',
                                                                               data=df,
                                                                               n=10,
                                                                               allowNull=True))

    with pytest.raises(AssertionError):
        assert all(multiple_columns.value_greater_equal_than_other_column_by_n(columnOne='hundreds',
                                                                               columnTwo='tens',
                                                                               data=df,
                                                                               n=None,
                                                                               allowNull=True))

    with pytest.raises(AssertionError):
        assert all(multiple_columns.value_greater_equal_than_other_column_by_n(columnOne='hundreds',
                                                                               columnTwo='tens',
                                                                               data=df,
                                                                               n='a',
                                                                               allowNull=True))


def test_value_less_than_other_column():
    df = pd.DataFrame({'hundreds': [200, 300, 400],
                       'hundreds2': [200, 300, 400],
                       'tens': [10, 20, 30],
                       'tens_with_nones': [10, None, 30],
                       'hundreds_with_nones': [100, None, 300],
                       'not_numbers': ['a', 'b', 'c'],
                       'none': None})

    assert not all(multiple_columns.value_less_than_other_column(columnOne='hundreds',
                                                                 columnTwo='tens',
                                                                 data=df,
                                                                 allowNull=False))

    assert not all(multiple_columns.value_less_than_other_column(columnOne='hundreds',
                                                                 columnTwo='hundreds2',
                                                                 data=df,
                                                                 allowNull=False))

    assert all(multiple_columns.value_less_than_other_column(columnOne='tens',
                                                             columnTwo='hundreds',
                                                             data=df,
                                                             allowNull=False))

    assert all(multiple_columns.value_less_than_other_column(columnOne='tens_with_nones',
                                                             columnTwo='hundreds_with_nones',
                                                             data=df,
                                                             allowNull=True))

    with pytest.raises(AssertionError):
        assert all(multiple_columns.value_less_than_other_column(columnOne='hundreds',
                                                                 columnTwo='not_numbers',
                                                                 data=df,
                                                                 allowNull=True))

    with pytest.raises(AssertionError):
        assert all(multiple_columns.value_less_than_other_column(columnOne='tens_with_nones',
                                                                 columnTwo='hundreds',
                                                                 data=df,
                                                                 allowNull=True))

    with pytest.raises(AssertionError):
        assert all(multiple_columns.value_less_than_other_column(columnOne='tens_with_nones',
                                                                 columnTwo='hundreds',
                                                                 data=df,
                                                                 allowNull=False))
    with pytest.raises(AssertionError):
        assert all(multiple_columns.value_less_than_other_column(columnOne='hundreds',
                                                                 columnTwo='none',
                                                                 data=df,
                                                                 allowNull=True))

    with pytest.raises(AssertionError):
        assert all(multiple_columns.value_less_than_other_column(columnOne='hundreds',
                                                                 columnTwo='hundreds',
                                                                 data=df,
                                                                 allowNull=False))


def test_value_less_equal_than_other_column():
    df = pd.DataFrame({'hundreds': [100, 300, 400],
                       'hundreds2': [100, 300, 400],
                       'tens': [100, 20, 30],
                       'tens_with_nones': [100, None, 30],
                       'hundreds_with_nones': [100, None, 300],
                       'not_numbers': ['a', 'b', 'c'],
                       'none': None})

    assert not all(multiple_columns.value_less_equal_than_other_column(columnOne='hundreds',
                                                                       columnTwo='tens',
                                                                       data=df,
                                                                       allowNull=False))

    assert all(multiple_columns.value_less_equal_than_other_column(columnOne='hundreds',
                                                                   columnTwo='hundreds2',
                                                                   data=df,
                                                                   allowNull=False))

    assert all(multiple_columns.value_less_equal_than_other_column(columnOne='tens',
                                                                   columnTwo='hundreds',
                                                                   data=df,
                                                                   allowNull=False))

    assert all(multiple_columns.value_less_equal_than_other_column(columnOne='tens_with_nones',
                                                                   columnTwo='hundreds_with_nones',
                                                                   data=df,
                                                                   allowNull=True))

    with pytest.raises(AssertionError):
        assert all(multiple_columns.value_less_equal_than_other_column(columnOne='hundreds',
                                                                       columnTwo='not_numbers',
                                                                       data=df,
                                                                       allowNull=True))

    with pytest.raises(AssertionError):
        assert all(multiple_columns.value_less_equal_than_other_column(columnOne='tens_with_nones',
                                                                       columnTwo='hundreds',
                                                                       data=df,
                                                                       allowNull=True))

    with pytest.raises(AssertionError):
        assert all(multiple_columns.value_less_equal_than_other_column(columnOne='tens_with_nones',
                                                                       columnTwo='hundreds',
                                                                       data=df,
                                                                       allowNull=False))
    with pytest.raises(AssertionError):
        assert all(multiple_columns.value_less_equal_than_other_column(columnOne='hundreds',
                                                                       columnTwo='none',
                                                                       data=df,
                                                                       allowNull=True))

    with pytest.raises(AssertionError):
        assert all(multiple_columns.value_less_equal_than_other_column(columnOne='hundreds',
                                                                       columnTwo='hundreds',
                                                                       data=df,
                                                                       allowNull=False))


def test_keys_identical_to_other_column():
    df = pd.DataFrame({'keys_identical_1': [{'aa': 'a', 'bb': 'b'},
                                            {'cc': 'aaa', 'dd': 'bbbb'},
                                            {'ee': 'ccc', 'ff': 'ddd'}],
                       'keys_identical_2': [{'aa': 'a1', 'bb': 'b2'},
                                            {'cc': 'aaa2', 'dd': 'bbb3b'},
                                            {'ee': 'ccc2', 'ff': 'd4dd'}],
                       'one_key_different': [{'aa1': 'a1', 'bb': 'b2'},
                                             {'cc': 'aaa2', 'dd': 'bbb3b'},
                                             {'ee': 'ccc2', 'ff': 'd4dd'}],
                       'different_keys': [{'aa2': 'a', 'bb2': 'b'},
                                          {'cc2': 'aaa', 'dd2': 'bbbb'},
                                          {'ee2': 'ccc', 'ff2': 'ddd'}],
                       'keys_identical_with_none_1': [{'aa2': 'a', 'bb2': 'b'},
                                                      None,
                                                      {'ee2': 'ccc', 'ff2': 'ddd'}],
                       'keys_identical_with_none_2': [{'aa2': 'a', 'bb2': 'b'},
                                                      None,
                                                      {'ee2': 'ccc', 'ff2': 'ddd'}],
                       'not_numbers': ['a', 'b', 'c'],
                       'none': None})

    assert all(multiple_columns.keys_identical_to_other_column(columnOne='keys_identical_1',
                                                               columnTwo='keys_identical_2',
                                                               data=df,
                                                               allowNull=False))

    assert all(multiple_columns.keys_identical_to_other_column(columnOne='keys_identical_with_none_1',
                                                               columnTwo='keys_identical_with_none_2',
                                                               data=df,
                                                               allowNull=True))

    assert not all(multiple_columns.keys_identical_to_other_column(columnOne='keys_identical_1',
                                                                   columnTwo='different_keys',
                                                                   data=df,
                                                                   allowNull=False))

    assert not all(multiple_columns.keys_identical_to_other_column(columnOne='keys_identical_1',
                                                                   columnTwo='one_key_different',
                                                                   data=df,
                                                                   allowNull=False))

    with pytest.raises(AssertionError):
        assert all(multiple_columns.keys_identical_to_other_column(columnOne='keys_identical_with_none_1',
                                                                   columnTwo='keys_identical_with_none_2',
                                                                   data=df,
                                                                   allowNull=False))

    with pytest.raises(AssertionError):
        assert all(multiple_columns.keys_identical_to_other_column(columnOne='keys_identical_1',
                                                                   columnTwo='not_numbers',
                                                                   data=df,
                                                                   allowNull=False))

    with pytest.raises(AssertionError):
        assert all(multiple_columns.keys_identical_to_other_column(columnOne='keys_identical_1',
                                                                   columnTwo='not_numbers',
                                                                   data=df,
                                                                   allowNull=False))


def test_keys_subset_of_other_column():
    df = pd.DataFrame({'keys_identical_1': [{'aa': 'a', 'bb': 'b'},
                                            {'cc': 'aaa', 'dd': 'bbbb'},
                                            {'ee': 'ccc', 'ff': 'ddd'}],
                       'keys_identical_2': [{'aa': 'a1', 'bb': 'b2', 'cc': 'cc'},
                                            {'cc': 'aaa2', 'dd': 'bbb3b', 'ccx': 'cc'},
                                            {'ee': 'ccc2', 'ff': 'd4dd', 'ccx': 'cc'}],
                       'one_key_different': [{'aa1': 'a1', 'bb': 'b2'},
                                             {'cc': 'aaa2', 'dd': 'bbb3b'},
                                             {'ee': 'ccc2', 'ff': 'd4dd'}],
                       'different_keys': [{'aa2': 'a', 'bb2': 'b'},
                                          {'cc2': 'aaa', 'dd2': 'bbbb'},
                                          {'ee2': 'ccc', 'ff2': 'ddd'}],
                       'keys_identical_with_none_1': [{'aa2': 'a', 'bb2': 'b'},
                                                      None,
                                                      {'ee2': 'ccc', 'ff2': 'ddd'}],
                       'keys_identical_with_none_2': [{'aa2': 'a', 'bb2': 'b'},
                                                      None,
                                                      {'ee2': 'ccc', 'ff2': 'ddd'}],
                       'not_numbers': ['a', 'b', 'c'],
                       'none': None})

    assert all(multiple_columns.keys_subset_of_other_column(columnOne='keys_identical_1',
                                                            columnTwo='keys_identical_2',
                                                            data=df,
                                                            allowNull=False))

    assert all(multiple_columns.keys_subset_of_other_column(columnOne='keys_identical_with_none_1',
                                                            columnTwo='keys_identical_with_none_2',
                                                            data=df,
                                                            allowNull=True))

    assert not all(multiple_columns.keys_subset_of_other_column(columnOne='keys_identical_1',
                                                                columnTwo='different_keys',
                                                                data=df,
                                                                allowNull=False))

    assert not all(multiple_columns.keys_subset_of_other_column(columnOne='keys_identical_1',
                                                                columnTwo='one_key_different',
                                                                data=df,
                                                                allowNull=False))

    with pytest.raises(AssertionError):
        assert all(multiple_columns.keys_subset_of_other_column(columnOne='keys_identical_with_none_1',
                                                                columnTwo='keys_identical_with_none_2',
                                                                data=df,
                                                                allowNull=False))

    with pytest.raises(AssertionError):
        assert all(multiple_columns.keys_subset_of_other_column(columnOne='keys_identical_1',
                                                                columnTwo='not_numbers',
                                                                data=df,
                                                                allowNull=False))

    with pytest.raises(AssertionError):
        assert all(multiple_columns.keys_subset_of_other_column(columnOne='keys_identical_1',
                                                                columnTwo='not_numbers',
                                                                data=df,
                                                                allowNull=False))


def test_keys_substring_of_other_column():
    df = pd.DataFrame({'keys_identical_1': [{'aa': 'a', 'bb': 'b'},
                                            {'cc': 'aaa', 'dd': 'bbbb'},
                                            {'ee': 'ccc', 'ff': 'ddd'}],
                       'keys_identical_1_with_extra': [{'aa': 'a', 'bb': 'b', 'c': 'cc'},
                                                       {'cc': 'aaa', 'dd': 'bbbb'},
                                                       {'ee': 'ccc', 'ff': 'ddd'}],
                       'keys_identical_2': [{'aab': 'a1', 'bbb': 'b2'},
                                            {'ccb': 'aaa2', 'ddb': 'bbb3b'},
                                            {'eeb': 'ccc2', 'ffb': 'd4dd'}],
                       'one_key_different': [{'ae1e': 'a1', 'bb': 'b2'},
                                             {'cc': 'aaa2', 'dd': 'bbb3b'},
                                             {'ee': 'ccc2', 'ff': 'd4dd'}],
                       'different_keys': [{'f': 'a', 'cxcx': 'b'},
                                          {'e': 'aaa', 'r': 'bbbb'},
                                          {'g': 'ccc', 'c': 'ddd'}],
                       'keys_identical_with_none_1': [{'aa2': 'a', 'bb2': 'b'},
                                                      None,
                                                      {'ee2': 'ccc', 'ff2': 'ddd'}],
                       'keys_identical_with_none_2': [{'aa2': 'a', 'bb2': 'b'},
                                                      None,
                                                      {'ee2': 'ccc', 'ff2': 'ddd'}],
                       'not_numbers': ['a', 'b', 'c'],
                       'none': None})

    assert all(multiple_columns.keys_substring_of_other_column(columnOne='keys_identical_1',
                                                               columnTwo='keys_identical_2',
                                                               data=df,
                                                               allowNull=False))

    assert not all(multiple_columns.keys_substring_of_other_column(columnOne='keys_identical_1_with_extra',
                                                                   columnTwo='keys_identical_1',
                                                                   data=df,
                                                                   allowNull=False))

    assert all(multiple_columns.keys_substring_of_other_column(columnOne='keys_identical_with_none_1',
                                                               columnTwo='keys_identical_with_none_2',
                                                               data=df,
                                                               allowNull=True))

    assert not all(multiple_columns.keys_substring_of_other_column(columnOne='keys_identical_1',
                                                                   columnTwo='different_keys',
                                                                   data=df,
                                                                   allowNull=False))

    assert not all(multiple_columns.keys_substring_of_other_column(columnOne='keys_identical_1',
                                                                   columnTwo='one_key_different',
                                                                   data=df,
                                                                   allowNull=False))

    with pytest.raises(AssertionError):
        assert all(multiple_columns.keys_substring_of_other_column(columnOne='keys_identical_with_none_1',
                                                                   columnTwo='keys_identical_with_none_2',
                                                                   data=df,
                                                                   allowNull=False))

    with pytest.raises(AssertionError):
        assert all(multiple_columns.keys_substring_of_other_column(columnOne='keys_identical_1',
                                                                   columnTwo='not_numbers',
                                                                   data=df,
                                                                   allowNull=False))

    with pytest.raises(AssertionError):
        assert all(multiple_columns.keys_substring_of_other_column(columnOne='keys_identical_1',
                                                                   columnTwo='not_numbers',
                                                                   data=df,
                                                                   allowNull=False))
