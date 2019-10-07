import pandas as pd
import numpy as np
import pytest

from mapy import single_column

defaultDF = pd.DataFrame({'not_null': [1, 2, None, 'amit', np.nan, 3],
                          'value_in_range': [1, 2, 3, 4, 50, 60],
                          'validate_value_length': ['amit', 'attias', 'a', 'v', 'b', 'c'],
                          'value_in_set': ['telaviv', 'paris', None, None, 'newyork', 'toronto'],
                          'sum_of_values_in_range': [{'ios': 3}, {'ios': 3, 'android': 4}, {'ios': 3, 'android': 4}, {},
                                                     None, {'ios': 3}],
                          'all_lower_case': ['amit', 'attias', 'a', None, 'b', 'c'],
                          'all_upper_case': ['AMIT', 'ATTIAS', 'AAA', 'VVV', 'CCC', 'SSSS']})


def test_value_in_set():
    df = pd.DataFrame({'value_in_set_no_null': ['telaviv', 'paris', 'newyork', 'toronto'],
                       'value_in_set_with_null': ['telaviv', 'paris', 'newyork', None],
                       'value_in_set_not_in_set': ['hi', 'paris', 'paris', 'paris']})

    assert all(single_column.value_in_set(data=df, column='value_in_set_no_null',
                                          setOfValues={'telaviv', 'paris', 'newyork', 'toronto'}, allowNull=False))
    assert all(single_column.value_in_set(data=df, column='value_in_set_with_null',
                                          setOfValues={'telaviv', 'paris', 'newyork', 'toronto'}, allowNull=True))
    assert not all(single_column.value_in_set(data=df, column='value_in_set_not_in_set',
                                              setOfValues={'telaviv', 'paris', 'newyork', 'toronto'}, allowNull=False))

    with pytest.raises(AssertionError):
        assert all(single_column.value_in_set(data=df, column='value_in_set_with_null',
                                              setOfValues={'telaviv', 'paris', 'newyork', 'toronto'}, allowNull=False))
    with pytest.raises(AssertionError):
        assert all(single_column.value_in_set(data=df, column='value_in_set_with_null', setOfValues={}, allowNull=True))

    with pytest.raises(AssertionError):
        assert all(
            single_column.value_in_set(data=df, column='value_in_set_with_null', setOfValues=None, allowNull=True))

    with pytest.raises(AssertionError):
        assert all(
            single_column.value_in_set(data=df, column='value_in_set_with_null', setOfValues='amit', allowNull=True))


def test_validate_value_length():
    df = pd.DataFrame({'validate_value_length_no_null': ['amit', 'attias', 'a', 'v', 'b', 'c'],
                       'validate_value_length_with_null': ['amit', 'attias', 'a', 'v', 'b', None],
                       'validate_value_length_all_valid_types': ['ami', [1, 2, 3], {1, 2, 3}, {'name': 'amit'}, 'b',
                                                                 'c'],
                       'validate_value_length_invalid_types': [4, [1, 2, 3], {1, 2, 3}, {'name': 'amit'}, 'b', 'c']})

    assert all(single_column.validate_value_length(data=df, column='validate_value_length_no_null',
                                                   desiredValueLengths={1, 4, 6, 7}, allowNull=False))
    assert all(single_column.validate_value_length(data=df, column='validate_value_length_with_null',
                                                   desiredValueLengths={1, 4, 6, 7}, allowNull=True))
    assert all(single_column.validate_value_length(data=df, column='validate_value_length_all_valid_types',
                                                   desiredValueLengths={1, 3}, allowNull=False))
    assert not all(
        single_column.validate_value_length(data=df, column='validate_value_length_no_null', desiredValueLengths={1, 3},
                                            allowNull=False))

    with pytest.raises(AssertionError):
        assert all(single_column.validate_value_length(data=df, column='validate_value_length_with_null',
                                                       desiredValueLengths={1, 4, 6, 7}, allowNull=False))

    with pytest.raises(AssertionError):
        assert all(single_column.validate_value_length(data=df, column='validate_value_length_invalid_types',
                                                       desiredValueLengths={1, 4, 6, 7}, allowNull=False))


def test_value_in_range():
    df = pd.DataFrame({'value_in_range_no_null': [1, 2, 3, 4, 50, 60],
                       'value_in_range_with_null': [1, 2, 3, 4, 50, None]})

    assert all(
        single_column.value_in_range(data=df, column='value_in_range_no_null', valueRange=(0, 60), allowNull=False))
    assert all(
        single_column.value_in_range(data=df, column='value_in_range_with_null', valueRange=(0, 60), allowNull=True))
    assert not all(
        single_column.value_in_range(data=df, column='value_in_range_no_null', valueRange=(0, 50), allowNull=False))

    with pytest.raises(AssertionError):
        assert all(single_column.value_in_range(data=df, column='value_in_range_with_null', valueRange=(0, 60),
                                                allowNull=False))


def test_all_keys_in_set():
    df = pd.DataFrame({'all_keys_in_set_empty_dict_with_null': [{'ios': 3}, {'ios': 3, 'android': 4},
                                                                {'ios': 3, 'android': 4}, {}, None, {'ios': 3}],
                       'all_keys_in_set_empty_dict_no_null': [{'ios': 3}, {'ios': 3, 'android': 4},
                                                              {'ios': 3, 'android': 4}, {}, {'ios': 3},
                                                              {'ios': 3}],
                       'all_keys_in_set_no_empty_dict': [{'ios': 3}, {'ios': 3, 'android': 4},
                                                         {'ios': 3, 'android': 4}, {'ios': 3, 'android': 4},
                                                         {'ios': 3, 'android': 4}, {'ios': 3}],
                       'not_all_keys_in_set': [{'ios': 3}, {'ios': 3, 'amit': 4}, {'ios': 3, 'android': 4},
                                               {}, None, {'ios': 3}],
                       'all_keys_in_set_corrupted': ['amit', {'ios': 3, 'amit': 4}, {'ios': 3, 'android': 4},
                                                     {}, None, {'ios': 3}]})

    assert all(single_column.all_keys_in_set(data=df, column='all_keys_in_set_empty_dict_with_null',
                                             setOfKeys={'ios', 'android'}, allowEmptyDict=True, allowNull=True))
    assert all(single_column.all_keys_in_set(data=df, column='all_keys_in_set_empty_dict_no_null',
                                             setOfKeys={'ios', 'android'}, allowEmptyDict=True, allowNull=False))
    assert all(
        single_column.all_keys_in_set(data=df, column='all_keys_in_set_no_empty_dict', setOfKeys={'ios', 'android'},
                                      allowEmptyDict=False, allowNull=False))

    with pytest.raises(AssertionError):
        assert all(single_column.all_keys_in_set(data=df, column='not_all_keys_in_set', setOfKeys={'ios', 'android'},
                                                 allowEmptyDict=True, allowNull=True))

    with pytest.raises(AssertionError):
        assert all(single_column.all_keys_in_set(data=df, column='all_keys_in_set_empty_dict_with_null',
                                                 setOfKeys={'ios', 'android'}, allowEmptyDict=False, allowNull=True))

    with pytest.raises(AssertionError):
        assert all(single_column.all_keys_in_set(data=df, column='all_keys_in_set_empty_dict_with_null',
                                                 setOfKeys={'ios', 'android'}, allowEmptyDict=True, allowNull=False))

    with pytest.raises(AssertionError):
        # setOfKeys is not iterable
        assert all(single_column.all_keys_in_set(data=df, column='all_keys_in_set_empty_dict_with_null',
                                                 setOfKeys='ios', allowEmptyDict=True, allowNull=True))

    with pytest.raises(AssertionError):
        assert all(single_column.all_keys_in_set(data=df, column='all_keys_in_set_corrupted',
                                                 setOfKeys={'ios', 'android'}, allowEmptyDict=True, allowNull=True))


def test_sum_of_values_in_range():
    df = pd.DataFrame({'sum_of_values_in_range_empty_dict_with_null': [{'ios': 3}, {'ios': 3, 'android': 4},
                                                                       {'ios': 3, 'android': 4}, {}, None, {'ios': 3}],
                       'sum_of_values_in_range_empty_dict_no_null': [{'ios': 3}, {'ios': 3, 'android': 4},
                                                                     {'ios': 3, 'android': 4}, {}, {'ios': 3},
                                                                     {'ios': 3}],
                       'sum_of_values_in_range_no_empty_dict': [{'ios': 3}, {'ios': 3, 'android': 4},
                                                                {'ios': 3, 'android': 4}, {'ios': 3, 'android': 4},
                                                                {'ios': 3, 'android': 4}, {'ios': 3}],
                       'not_sum_of_values_in_range': [{'ios': 3}, {'ios': 3, 'android': 4}, {'ios': 3, 'android': 4},
                                                      {}, None, {'ios': 3}]})

    assert all(single_column.sum_of_values_in_range(data=df, column='sum_of_values_in_range_empty_dict_with_null',
                                                    valueRange=(3, 8), allowEmptyDict=True, allowNull=True))
    assert all(single_column.sum_of_values_in_range(data=df, column='sum_of_values_in_range_empty_dict_no_null',
                                                    valueRange=(3, 8), allowEmptyDict=True, allowNull=False))
    assert all(
        single_column.sum_of_values_in_range(data=df, column='sum_of_values_in_range_no_empty_dict', valueRange=(3, 8),
                                             allowEmptyDict=False, allowNull=False))

    with pytest.raises(AssertionError):
        assert all(single_column.sum_of_values_in_range(data=df, column='not_sum_of_values_in_range', valueRange=(3, 4),
                                                        allowEmptyDict=True, allowNull=True))

    with pytest.raises(AssertionError):
        assert all(single_column.sum_of_values_in_range(data=df, column='sum_of_values_in_range_empty_dict_with_null',
                                                        valueRange=(3, 8), allowEmptyDict=False, allowNull=True))

    with pytest.raises(AssertionError):
        assert all(single_column.sum_of_values_in_range(data=df, column='sum_of_values_in_range_empty_dict_with_null',
                                                        valueRange=(3, 8), allowEmptyDict=True, allowNull=False))


def test_all_lower_case():
    df = pd.DataFrame({'all_lower_case_no_null': ['amit', 'attias', 'aaa'],
                       'all_lower_case_with_null': ['amit', 'attias', None],
                       'not_all_lower_case_no_null': ['amit', 'AtTias', 'AAaa'],
                       'not_all_lower_case_with_null': ['amit', 'AtTiaS', None]})

    assert all(single_column.all_lower_case(data=df, column='all_lower_case_no_null', allowNull=False))
    assert all(single_column.all_lower_case(data=df, column='all_lower_case_with_null', allowNull=True))

    with pytest.raises(AssertionError):
        assert all(single_column.all_lower_case(data=df, column='not_all_lower_case_no_null', allowNull=False))

    with pytest.raises(AssertionError):
        assert all(single_column.all_lower_case(data=df, column='not_all_lower_case_with_null', allowNull=True))

    with pytest.raises(AssertionError):
        assert all(single_column.all_lower_case(data=df, column='all_lower_case_with_null', allowNull=False))

    with pytest.raises(AssertionError):
        assert all(single_column.all_lower_case(data=df, column='not_all_lower_case_with_null', allowNull=False))


def test_all_upper_case():
    df = pd.DataFrame({'all_upper_case_no_null': ['AMIT', 'ATTIAS', 'AAA'],
                       'all_upper_case_with_null': ['AMIT', 'ATTIAS', None],
                       'not_all_upper_case_no_null': ['AMIT', 'AtTIAS', 'AAaa'],
                       'not_all_upper_case_with_null': ['AMIT', 'AtTIAS', None]})

    assert all(single_column.all_upper_case(data=df, column='all_upper_case_no_null', allowNull=False))
    assert all(single_column.all_upper_case(data=df, column='all_upper_case_with_null', allowNull=True))

    with pytest.raises(AssertionError):
        assert all(single_column.all_upper_case(data=df, column='not_all_upper_case_no_null', allowNull=False))

    with pytest.raises(AssertionError):
        assert all(single_column.all_upper_case(data=df, column='not_all_upper_case_with_null', allowNull=True))

    with pytest.raises(AssertionError):
        assert all(single_column.all_upper_case(data=df, column='all_upper_case_with_null', allowNull=False))

    with pytest.raises(AssertionError):
        assert all(single_column.all_upper_case(data=df, column='not_all_upper_case_with_null', allowNull=False))


def test_not_null():
    df = pd.DataFrame({'not_null': ['AMIT', 'ATTIAS', 'AAA'],
                       'contains_null': ['AMIT', 'ATTIAS', None],
                       'invalid_types': [(), 'AtTIAS', 'AAaa'],
                       'not_all_upper_case_with_null': ['AMIT', 'AtTIAS', None]})

    assert all(single_column.not_null(data=df, column='not_null'))
    assert not all(single_column.not_null(data=df, column='contains_null'))

    with pytest.raises(AssertionError):
        assert all(single_column.not_null(data=df, column='invalid_types'))
    #
    # with pytest.raises(AssertionError):
    #     assert all(single_column.all_upper_case(data=df, column='not_all_upper_case_with_null', allowNull=True))
    #
    # with pytest.raises(AssertionError):
    #     assert all(single_column.all_upper_case(data=df, column='all_upper_case_with_null', allowNull=False))
    #
    # with pytest.raises(AssertionError):
    #     assert all(single_column.all_upper_case(data=df, column='not_all_upper_case_with_null', allowNull=False))
