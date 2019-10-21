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
    input_dt_german_credit_card_uci


def input_df():
    features = [
        [1.43749224, 2.31180576, 0.80017904, 2.88098529],
        [0.77583347, 0.59433006, 0.73031927, 0.26679244],
        [2.53661484, 0.364639, 0.93174688, 1.41004666],
        [-1.44004145, 1.19072726, -0.86714616, 1.29939681],
    ]
    label = [1, 0, 1, 0]
    df = pd.DataFrame(data=features, columns=["f1", "f2", "f3", "f4"])
    df["label"] = label
    df["f5"] = pd.Series(['Male', 'Female', 'Child', 'Female'])
    return df


def input_dt():
    return DataTable(df=input_df())


def input_dt_categorical():
    df = input_df()
    df["label"] = [True, False, True, False]
    categorical_fea = pd.Series(['Male', 'Female', 'Child', 'Female']).astype('category')
    df["f5"] = categorical_fea
    return DataTable(df=df)


def input_dt_str_target():
    df = input_df()
    date_time_series = pd.Series(['20111230', '20111130', '20121230', '20131230'])
    time_span_series = pd.Series(np.arange(4))
    df["label"] = ['T1', 'F1', 'T1', 'F1']
    df["f5"] = pd.Series(['Male', 'Female', 'Child', 'Female']).astype('category')
    df["f6"] = convert_column_by_element_type(date_time_series, ElementTypeName.DATETIME)
    df["f7"] = convert_column_by_element_type(time_span_series, ElementTypeName.TIMESPAN, time_span_format='h')
    df["f8"] = pd.Series([np.nan, np.nan, np.nan, np.nan])
    return DataTable(df=df)


def input_with_nan_dt():
    df = input_df()
    df["f4"][2] = np.nan
    return DataTable(df=df)


def test_success():
    csb = DataTableColumnSelectionBuilder()
    column_selection = csb.include_col_names('label').build()
    scoring_method = FilterBasedFeatureSelectionScoringMethod.PearsonCorrelation
    filtered_dataset, features = FilterBasedFeatureSelectionModule.run(
        dataset=input_dt(),
        feature_only=True,
        column_select=column_selection,
        req_feature_count=2,
        method=scoring_method
    )
    expected_pearson_features_dt = DataTable(
        pd.DataFrame([[1.0, 0.79840152, 0.73126409, 0.63610694, 0.29567297, 0]],
                     columns=['label', 'f1', 'f4', 'f3', 'f2', 'f5']))
    np.testing.assert_array_almost_equal(features.data_frame.values, expected_pearson_features_dt.data_frame.values)
    assert features.meta_data.column_attributes.names == expected_pearson_features_dt.meta_data.column_attributes.names
    assert filtered_dataset.column_names == expected_pearson_features_dt.column_names[:3]


def test_success_categorical_feature():
    csb = DataTableColumnSelectionBuilder()
    column_selection = csb.include_col_names('label').build()
    scoring_method = FilterBasedFeatureSelectionScoringMethod.PearsonCorrelation
    filtered_dataset, features = FilterBasedFeatureSelectionModule.run(
        dataset=input_dt_categorical(),
        feature_only=True,
        column_select=column_selection,
        req_feature_count=2,
        method=scoring_method
    )
    expected_features_dt = DataTable(
        pd.DataFrame([[1.0, 1.0, 0.79840152, 0.73126409, 0.63610694, 0.29567297]],
                     columns=['label', 'f5', 'f1', 'f4', 'f3', 'f2']))
    np.testing.assert_array_almost_equal(features.data_frame.values, expected_features_dt.data_frame.values)
    assert features.meta_data.column_attributes.names == expected_features_dt.meta_data.column_attributes.names
    assert filtered_dataset.column_names == expected_features_dt.column_names[:3]


def test_success_convert_str_target_to_categorical():
    csb = DataTableColumnSelectionBuilder()
    column_selection = csb.include_col_names('label').build()
    scoring_method = FilterBasedFeatureSelectionScoringMethod.PearsonCorrelation
    filtered_dataset, features = FilterBasedFeatureSelectionModule.run(
        dataset=input_dt_str_target(),
        feature_only=True,
        column_select=column_selection,
        req_feature_count=2,
        method=scoring_method
    )
    expected_features_dt = DataTable(
        pd.DataFrame([[1.0, 0.79840152, 0.73126409, 0.63610694, 0.447214, 0.29567297, 0.270093, 0, 0]],
                     columns=['label', 'f1', 'f4', 'f3', 'f7', 'f2', 'f6', 'f5', 'f8']))
    np.testing.assert_array_almost_equal(features.data_frame.values, expected_features_dt.data_frame.values)
    assert features.meta_data.column_attributes.names == expected_features_dt.meta_data.column_attributes.names
    assert filtered_dataset.column_names == expected_features_dt.column_names[:3]


def test_success_pearson_with_nan():
    csb = DataTableColumnSelectionBuilder()
    column_selection = csb.include_col_names('label').build()
    scoring_method = FilterBasedFeatureSelectionScoringMethod.PearsonCorrelation
    filtered_dataset, features = FilterBasedFeatureSelectionModule.run(
        dataset=input_with_nan_dt(),
        feature_only=True,
        column_select=column_selection,
        req_feature_count=2,
        method=scoring_method
    )
    expected_with_nan_features_dt = DataTable(
        pd.DataFrame([[1.0, 0.79840152, 0.63610694, 0.29567297, 0, 0]],
                     columns=['label', 'f1', 'f3', 'f2', 'f4', 'f5']))
    np.testing.assert_array_almost_equal(features.data_frame.values,
                                         expected_with_nan_features_dt.data_frame.values)
    assert features.meta_data.column_attributes.names == expected_with_nan_features_dt.meta_data. \
        column_attributes.names
    assert filtered_dataset.column_names == expected_with_nan_features_dt.column_names[:3]


def test_success_absolute_co_eff():
    csb = DataTableColumnSelectionBuilder()
    column_selection = csb.include_col_names('Credit risk').build()
    scoring_method = FilterBasedFeatureSelectionScoringMethod.PearsonCorrelation
    # scoring_method = FilterBasedFeatureSelectionScoringMethod.ChiSquared
    filtered_dataset, features = FilterBasedFeatureSelectionModule.run(
        dataset=input_dt_german_credit_card_uci(),
        feature_only=True,
        column_select=column_selection,
        req_feature_count=2,
        method=scoring_method
    )
    expected_pearson_features_dt = DataTable(
        pd.DataFrame([[1, 0.254343, 0.146241, 0.123237, 0.08287, 0.012475, 0.010219, 0.006686,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]],
                     columns=[
                         'Credit risk', 'Age in years', 'Duration in months',
                         'Number of people being liable to provide maintenance for',
                         'Credit amount', 'Number of existing credits at this bank',
                         'Installment rate in percentage of disposable income', 'Present residence since',
                         'Telephone', 'Job', 'Housing', 'Other installment plans', 'Status of checking account',
                         'Property', 'Other debtors/guarantors', 'Personal status and sex',
                         'Present employment since', 'Savings account/bond', 'Purpose',
                         'Credit history', 'Foreign worker'
                     ]))

    np.testing.assert_array_almost_equal(features.data_frame.values, expected_pearson_features_dt.data_frame.values)
    assert features.meta_data.column_attributes.names == expected_pearson_features_dt.meta_data.column_attributes.names
    assert filtered_dataset.column_names == expected_pearson_features_dt.column_names[:3]


def test_error_desired_feature_cnt():
    csb = DataTableColumnSelectionBuilder()
    column_selection = csb.include_col_names('label').build()
    scoring_method = FilterBasedFeatureSelectionScoringMethod.PearsonCorrelation
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
    column_selection = csb.include_col_names('label', 'f1').build()
    scoring_method = FilterBasedFeatureSelectionScoringMethod.PearsonCorrelation
    with pytest.raises(UnexpectedNumberOfColumnsError):
        FilterBasedFeatureSelectionModule.run(
            dataset=input_dt(),
            feature_only=True,
            column_select=column_selection,
            req_feature_count=2,
            method=scoring_method
        )
