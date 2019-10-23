import numpy as np
import pandas as pd
import pytest

from azureml.studio.common.datatable.constants import ElementTypeName
from azureml.studio.common.datatable.data_table import DataTable
from azureml.studio.common.datatable.data_table import DataTableColumnSelectionBuilder
from azureml.studio.common.datatable.data_type_conversion import convert_column_by_element_type
from azureml.studio.common.error import UnexpectedNumberOfColumnsError, GreaterThanOrEqualToError
from azureml.studio.modules.feature_selection.filter_based_feature_selection.filter_based_feature_selection import \
    FilterBasedFeatureSelectionScoringMethod, FilterBasedFeatureSelectionModule
from azureml.studio.modules.feature_selection.filter_based_feature_selection.test.input import \
    input_dt_german_credit_card_uci, input_dt_adult_census_income


def input_dt():
    df = pd.DataFrame({
        'purpose': ['credit_car', 'car', 'small_business', 'other', 'other', 'wedding',
                    'debt_consolidation', 'car', 'small_business', 'other'],
        'sub_grade': ['B2', 'C4', 'C5', 'C1', 3, 'A4', 'C5', 'E1', 'F2', np.nan],
        'grade': ['B', 'C', 'C', 'C', 'B', 'A', 'C', 'E', 'F', 'B'],
        'loan_status': ['Fully Paid', 'Charged Off', 'Fully Paid', 'Fully Paid', 'Fully Paid',
                        'Fully Paid', 'Fully Paid', 'Fully Paid', 'Charged Off', 'Charged Off'],
        'f1': [1, 0, 1, 1, 1, 1, 0, 1, 0, 0],
        'f0': [2.53, 0.36, -0.93, 1.41, 2.53, np.nan, 0.93, 1.41, 2.53, -0.36]
    })
    date_time_series = pd.Series(['20111230', '20111130', '20121230', '20131230', '20131229',
                                  '20131228', '20131120', '20130120'])
    time_span_series = pd.Series(np.arange(10))
    df["f6"] = convert_column_by_element_type(date_time_series, ElementTypeName.DATETIME)
    df["f7"] = convert_column_by_element_type(time_span_series, ElementTypeName.TIMESPAN, time_span_format='h')
    return DataTable(df=df)


def input_nan_dt():
    df = pd.DataFrame({
        'loan_status': ['Fully Paid', 'Charged Off', 'Fully Paid', 'Fully Paid',
                        np.nan, np.nan, np.nan, np.nan],
        'f1': [np.nan, np.nan, np.nan, np.nan, 1, 1, 0, 1],
        'f2': [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
        'f3': ['B2', 'C4', 'C5', 'C1', 'B5', 'A4', 'C5', 'E1']
    })
    return DataTable(df=df)


def input_dt_diff_between_numeric_and_str():
    dt = input_dt_adult_census_income()
    df = dt.data_frame
    df['fnlwgt_str'] = convert_column_by_element_type(df['fnlwgt'], ElementTypeName.STRING)
    df_to_compare = df[['income', 'fnlwgt', 'fnlwgt_str']]
    return DataTable(df_to_compare)


def test_success():
    csb = DataTableColumnSelectionBuilder()
    column_selection = csb.include_col_names('loan_status').build()
    req_feature_count = 2
    scoring_method = FilterBasedFeatureSelectionScoringMethod.ChiSquared
    filtered_dataset, features = FilterBasedFeatureSelectionModule.run(
        dataset=input_dt(),
        feature_only=True,
        column_select=column_selection,
        req_feature_count=req_feature_count,
        method=scoring_method
    )
    expected_features_dt = DataTable(
        pd.DataFrame([[1, 10, 9, 8, 6.428571, 6, 3.253968, 2.063492]],
                     columns=['loan_status', 'f7', 'sub_grade', 'f6',
                              'f1', 'f0', 'grade', 'purpose']))
    np.testing.assert_array_almost_equal(features.data_frame.values, expected_features_dt.data_frame.values)
    assert features.meta_data.column_attributes.names == expected_features_dt.meta_data.column_attributes.names
    assert filtered_dataset.column_names == expected_features_dt.column_names[:req_feature_count + 1]


def test_success_empty_contingency():
    csb = DataTableColumnSelectionBuilder()
    column_selection = csb.include_col_names('loan_status').build()
    req_feature_count = 2
    scoring_method = FilterBasedFeatureSelectionScoringMethod.ChiSquared
    filtered_dataset, features = FilterBasedFeatureSelectionModule.run(
        dataset=input_nan_dt(),
        feature_only=True,
        column_select=column_selection,
        req_feature_count=req_feature_count,
        method=scoring_method
    )
    expected_features_dt = DataTable(
        pd.DataFrame([[1, 4, 0, 0]], columns=['loan_status', 'f3', 'f1', 'f2']))
    np.testing.assert_array_almost_equal(features.data_frame.values, expected_features_dt.data_frame.values)
    assert features.meta_data.column_attributes.names == expected_features_dt.meta_data.column_attributes.names
    assert filtered_dataset.column_names == expected_features_dt.column_names[:req_feature_count + 1]


def test_success_features_with_numerical():
    csb = DataTableColumnSelectionBuilder()
    column_selection = csb.include_col_names('income').build()
    req_feature_count = 5
    scoring_method = FilterBasedFeatureSelectionScoringMethod.ChiSquared
    filtered_dataset, features = FilterBasedFeatureSelectionModule.run(
        dataset=input_dt_adult_census_income(),
        feature_only=True,
        column_select=column_selection,
        req_feature_count=req_feature_count,
        method=scoring_method
    )
    expected_features_dt = DataTable(
        pd.DataFrame([[1, 40.870098, 39.08399, 34.07646, 31.481156, 29.422486,
                       26.857885, 20.921428, 20.425017, 16.716968, 16.489103,
                       4.888783, 4.754953, 3.464461, 3.444782]],
                     columns=['income', 'education', 'education-num', 'occupation', 'relationship',
                              'marital-status', 'age', 'capital-gain', 'native-country', 'hours-per-week',
                              'workclass', 'race', 'capital-loss', 'fnlwgt', 'sex']))
    np.testing.assert_array_almost_equal(features.data_frame.values, expected_features_dt.data_frame.values)
    assert features.meta_data.column_attributes.names == expected_features_dt.meta_data.column_attributes.names
    assert filtered_dataset.column_names == expected_features_dt.column_names[:req_feature_count + 1]


def test_success_numerical_label():
    csb = DataTableColumnSelectionBuilder()
    column_selection = csb.include_col_names('fnlwgt').build()
    req_feature_count = 5
    scoring_method = FilterBasedFeatureSelectionScoringMethod.ChiSquared
    filtered_dataset, features = FilterBasedFeatureSelectionModule.run(
        dataset=input_dt_adult_census_income(),
        feature_only=True,
        column_select=column_selection,
        req_feature_count=req_feature_count,
        method=scoring_method
    )
    # column 'capital-loss', 'capital-gain' is sparse series
    expected_features_dt = DataTable(
        pd.DataFrame([[1, 156.101786, 103.379895, 93.326563, 87.252655,
                       86.367768, 83.893269, 57.61446, 50.926342, 50.323583,
                       47.150222, 38.781378, 38.329334, 4.027636, 3.464461]],
                     columns=['fnlwgt', 'marital-status', 'hours-per-week', 'occupation', 'age', 'education',
                              'native-country', 'capital-loss', 'relationship', 'education-num', 'race',
                              'workclass', 'capital-gain', 'sex', 'income']))
    np.testing.assert_array_almost_equal(features.data_frame.values, expected_features_dt.data_frame.values)
    assert features.meta_data.column_attributes.names == expected_features_dt.meta_data.column_attributes.names
    assert filtered_dataset.column_names == expected_features_dt.column_names[:req_feature_count + 1]


def test_success_diff_between_numeric_and_str():
    csb = DataTableColumnSelectionBuilder()
    column_selection = csb.include_col_names('income').build()
    req_feature_count = 5
    scoring_method = FilterBasedFeatureSelectionScoringMethod.ChiSquared
    filtered_dataset, features = FilterBasedFeatureSelectionModule.run(
        dataset=input_dt_diff_between_numeric_and_str(),
        feature_only=True,
        column_select=column_selection,
        req_feature_count=req_feature_count,
        method=scoring_method
    )
    expected_features_dt = DataTable(
        pd.DataFrame([[1, 200, 3.464461]], columns=['income', 'fnlwgt_str', 'fnlwgt']))
    np.testing.assert_array_almost_equal(features.data_frame.values, expected_features_dt.data_frame.values)
    assert features.meta_data.column_attributes.names == expected_features_dt.meta_data.column_attributes.names
    assert filtered_dataset.column_names == expected_features_dt.column_names[:req_feature_count + 1]


def test_success_imbalance_binary_label_series():
    csb = DataTableColumnSelectionBuilder()
    column_selection = csb.include_col_names('Credit risk').build()
    scoring_method = FilterBasedFeatureSelectionScoringMethod.ChiSquared
    filtered_dataset, features = FilterBasedFeatureSelectionModule.run(
        dataset=input_dt_german_credit_card_uci(),
        feature_only=True,
        column_select=column_selection,
        req_feature_count=2,
        method=scoring_method
    )
    expected_pearson_features_dt = DataTable(
        pd.DataFrame([[1, 13.872354, 10.907974, 9.710841, 8.513709, 6.49093,
                       6.473751, 5.522487, 5.428259, 5.115486, 4.327564, 3.813933,
                       2.940988, 2.168367, 1.223545, 1.105442, 0.759374, 0.43277,
                       0.329255, 0.194707, 0]],
                     columns=[
                         'Credit risk', 'Purpose', 'Age in years', 'Duration in months', 'Present employment since',
                         'Credit history', 'Credit amount', 'Personal status and sex', 'Savings account/bond',
                         'Present residence since', 'Status of checking account', 'Other installment plans', 'Job',
                         'Housing', 'Number of existing credits at this bank', 'Property',
                         'Number of people being liable to provide maintenance for', 'Other debtors/guarantors',
                         'Installment rate in percentage of disposable income', 'Telephone', 'Foreign worker'
                     ]))

    np.testing.assert_array_almost_equal(features.data_frame.values, expected_pearson_features_dt.data_frame.values)
    assert features.meta_data.column_attributes.names == expected_pearson_features_dt.meta_data.column_attributes.names
    assert filtered_dataset.column_names == expected_pearson_features_dt.column_names[:3]


def test_error_desired_feature_cnt():
    csb = DataTableColumnSelectionBuilder()
    column_selection = csb.include_col_names('loan_status').build()
    scoring_method = FilterBasedFeatureSelectionScoringMethod.ChiSquared
    with pytest.raises(GreaterThanOrEqualToError):
        FilterBasedFeatureSelectionModule.run(
            dataset=input_dt(),
            feature_only=True,
            column_select=column_selection,
            req_feature_count=0,
            method=scoring_method
        )


def test_error_multi_target_column():
    csb = DataTableColumnSelectionBuilder()
    column_selection = csb.include_col_names('loan_status', 'f1').build()
    scoring_method = FilterBasedFeatureSelectionScoringMethod.ChiSquared
    with pytest.raises(UnexpectedNumberOfColumnsError):
        FilterBasedFeatureSelectionModule.run(
            dataset=input_dt(),
            feature_only=True,
            column_select=column_selection,
            req_feature_count=2,
            method=scoring_method
        )
