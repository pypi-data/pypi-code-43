import numbers
import random

import numpy as np
import pandas as pd
import pytest

import azureml.studio.common.error as error_setting
from azureml.studio.common.datatable.data_table import DataTable
from azureml.studio.modules.ml.common.constants import ScoreColumnConstants
from azureml.studio.modules.ml.evaluate.evaluate_generic_module.evaluate_generic_module import EvaluateModelModule
from azureml.studio.modules.ml.initialize_models.evaluator import BinaryClassificationEvaluator


def _get_binary_score_columns():
    return {
        ScoreColumnConstants.BinaryClassScoredLabelType: ScoreColumnConstants.ScoredLabelsColumnName,
        ScoreColumnConstants.CalibratedScoreType: ScoreColumnConstants.ScoredProbabilitiesColumnName
    }


def _get_multi_score_columns():
    return {
        ScoreColumnConstants.MultiClassScoredLabelType: ScoreColumnConstants.ScoredLabelsColumnName,
    }


def _get_regression_columns():
    return {
        ScoreColumnConstants.RegressionScoredLabelType: ScoreColumnConstants.ScoredLabelsColumnName,
    }


def _get_legal_binary_data():
    data_table = DataTable(pd.DataFrame(
        {
            'Label': ['pos', 'neg', 'pos', 'neg', None],
            ScoreColumnConstants.ScoredProbabilitiesColumnName: [0.9, 0.1, 0.4, 0.6, 0.7],
            ScoreColumnConstants.ScoredLabelsColumnName: ['pos', 'neg', 'neg', 'pos', 'neg'],
        }
    ))
    return data_table


def _get_illegal_allna_binary_data():
    data_table = DataTable(pd.DataFrame(
        {
            'Label': [None, None, np.nan, np.nan, None],
            ScoreColumnConstants.ScoredProbabilitiesColumnName: [0.9, 0.1, 0.4, 0.6, 0.7],
            ScoreColumnConstants.ScoredLabelsColumnName: ['pos', 'neg', 'neg', 'pos', 'neg'],
        }
    ))
    return data_table


def _get_pos_label_binary_data():
    data_table = DataTable(pd.DataFrame(
        {
            'Label': [1, 1, 1, 1, 1],
            ScoreColumnConstants.ScoredProbabilitiesColumnName: [0.9, 0.1, 0.4, 0.6, 0.7],
            ScoreColumnConstants.ScoredLabelsColumnName: [1, 0, 0, 1, 1],
        }
    ))
    return data_table


def _get_neg_label_binary_data():
    data_table = DataTable(pd.DataFrame(
        {
            'Label': [0, 0, 0, 0, 0],
            ScoreColumnConstants.ScoredProbabilitiesColumnName: [0.9, 0.1, 0.4, 0.6, 0.7],
            ScoreColumnConstants.ScoredLabelsColumnName: [1, 0, 0, 1, 1],
        }
    ))
    return data_table


def _get_all_pos_binary_data():
    data_table = DataTable(pd.DataFrame(
        {
            'Label': [1, 1, 1, 1, 1],
            ScoreColumnConstants.ScoredProbabilitiesColumnName: [0.9, 0.8, 0.7, 0.6, 0.7],
            ScoreColumnConstants.ScoredLabelsColumnName: [1, 1, 1, 1, 1],
        }
    ))
    return data_table


def _get_all_neg_binary_data():
    data_table = DataTable(pd.DataFrame(
        {
            'Label': [0, 0, 0, 0, 0],
            ScoreColumnConstants.ScoredProbabilitiesColumnName: [0.1, 0.2, 0.1, 0.4, 0.3],
            ScoreColumnConstants.ScoredLabelsColumnName: [0, 0, 0, 0, 0],
        }
    ))
    return data_table


def _get_legal_multi_data():
    data_table = DataTable(pd.DataFrame(
        {
            'Label': ['pos', 'neg', 'pos', 'neu', None],
            ScoreColumnConstants.ScoredLabelsColumnName: ['pos', 'neu', 'neg', 'pos', 'neg'],
        }
    ))
    return data_table


def _get_illegal_allna_multi_data():
    data_table = DataTable(pd.DataFrame(
        {
            'Label': [None, None, np.nan, np.nan, None],
            ScoreColumnConstants.ScoredLabelsColumnName: ['pos', 'neu', 'neg', 'pos', 'neg'],
        }
    ))
    return data_table


def _get_legal_regression_data():
    data_table = DataTable(pd.DataFrame(
        {
            'Label': [1.2, 2.3, 5.6, 10.1, None],
            ScoreColumnConstants.ScoredLabelsColumnName: [1.3, 2.3, 4.2, 4.5, 10.0],
        }
    ))
    return data_table


def _get_illegal_allna_regression_data():
    data_table = DataTable(pd.DataFrame(
        {
            'Label': [None, None, np.nan, np.nan, None],
            ScoreColumnConstants.ScoredLabelsColumnName: [1.3, 2.3, 4.2, 4.5, 10.0],
        }
    ))
    return data_table


def _get_legal_binary_scored_data():
    data_table = _get_legal_binary_data()
    data_table.meta_data.label_column_name = 'Label'
    data_table.meta_data.score_column_names = _get_binary_score_columns()
    return data_table.clone()


def _get_illegal_allna_binary_scored_data():
    data_table = _get_illegal_allna_binary_data()
    data_table.meta_data.label_column_name = 'Label'
    data_table.meta_data.score_column_names = _get_binary_score_columns()
    return data_table.clone()


def _get_legal_multi_scored_data():
    data_table = _get_legal_multi_data()
    data_table.meta_data.label_column_name = 'Label'
    data_table.meta_data.score_column_names = _get_multi_score_columns()
    return data_table.clone()


def _get_illegal_allna_multi_scored_data():
    data_table = _get_illegal_allna_multi_data()
    data_table.meta_data.label_column_name = 'Label'
    data_table.meta_data.score_column_names = _get_multi_score_columns()
    return data_table.clone()


def _get_legal_regression_scored_data():
    data_table = _get_legal_regression_data()
    data_table.meta_data.label_column_name = 'Label'
    data_table.meta_data.score_column_names = _get_regression_columns()
    return data_table.clone()


def _get_illegal_allna_regression_scored_data():
    data_table = _get_illegal_allna_regression_data()
    data_table.meta_data.label_column_name = 'Label'
    data_table.meta_data.score_column_names = _get_regression_columns()
    return data_table.clone()


def _get_illegal_extra_label_binary_scored_data():
    legal_label_pool = ['0', '1']
    illegal_label_pool = ['2', '3']
    sample_num = 20

    # generate labels
    # the illegal label column at least contain one illegal label
    labels = [random.choice(illegal_label_pool)]
    labels += random.choices(legal_label_pool + illegal_label_pool, k=sample_num - 1)

    # generate scored labels
    scored_labels = random.choices(legal_label_pool, k=sample_num)

    # generate probabilities
    probabilities = [0.1 + int(scored_labels[i]) * 0.5 for i in range(sample_num)]

    data_table = DataTable(pd.DataFrame(
        {
            'Label': labels,
            ScoreColumnConstants.ScoredProbabilitiesColumnName: probabilities,
            ScoreColumnConstants.ScoredLabelsColumnName: scored_labels
        }
    ))
    data_table.meta_data.label_column_name = 'Label'
    data_table.meta_data.score_column_names = _get_binary_score_columns()

    return data_table


@pytest.mark.parametrize(
    'data_table',
    [
        (_get_legal_binary_data()),
        (_get_legal_multi_data()),
        (_get_legal_regression_data())
    ]
)
def test_evaluate_not_scored_meta_data(data_table):
    data_table.meta_data.label_column_name = 'Label'
    with pytest.raises(error_setting.NotScoredDatasetError):
        EvaluateModelModule.run(
            scored_data=data_table,
            scored_data_to_compare=None)


@pytest.mark.parametrize(
    'scored_data, scored_data_to_compare, error_dataset_name',
    [
        (_get_legal_binary_scored_data(), _get_illegal_allna_binary_scored_data(), "Scored dataset to compare"),
        (_get_illegal_allna_binary_scored_data(), _get_legal_binary_scored_data(), "Scored dataset"),
        (_get_legal_multi_scored_data(), _get_illegal_allna_multi_scored_data(), "Scored dataset to compare"),
        (_get_illegal_allna_multi_scored_data(), _get_legal_multi_scored_data(), "Scored dataset"),
        (_get_legal_regression_scored_data(), _get_illegal_allna_regression_scored_data(), "Scored dataset to compare"),
        (_get_illegal_allna_regression_scored_data(), _get_legal_regression_scored_data(), "Scored dataset"),
    ]
)
def test_received_all_nan_labeled(scored_data, scored_data_to_compare, error_dataset_name):
    with pytest.raises(expected_exception=error_setting.LabelColumnDoesNotHaveLabeledPointsError,
                       match=f"Exception occurs when label column in dataset {error_dataset_name} "
                             f"is missing or has less than 1 labeled rows."):
        EvaluateModelModule.run(scored_data=scored_data, scored_data_to_compare=scored_data_to_compare)


# region for binary classification
def test_received_only_neg_label_data():
    data_table = _get_neg_label_binary_data()
    data_table.meta_data.label_column_name = 'Label'
    data_table.meta_data.score_column_names = _get_binary_score_columns()
    scored_data = EvaluateModelModule.run(
        scored_data=data_table,
        scored_data_to_compare=None)[0]
    metric_dict = scored_data.data.data_frame.iloc[0].to_dict()
    assert np.isclose(a=metric_dict['AUC'], b=0.0, rtol=1e-9)
    assert np.isclose(a=metric_dict['Accuracy'], b=0.4, rtol=1e-9)
    assert np.isclose(a=metric_dict['Precision'], b=0.0, rtol=1e-9)
    assert np.isclose(a=metric_dict['Recall'], b=0.0, rtol=1e-9)
    assert metric_dict['True Positive'] == 0
    assert metric_dict['True Negative'] == 2
    assert metric_dict['False Negative'] == 0
    assert metric_dict['False Positive'] == 3


def test_received_only_pos_label_data():
    data_table = _get_pos_label_binary_data()
    data_table.meta_data.label_column_name = 'Label'
    data_table.meta_data.score_column_names = _get_binary_score_columns()
    scored_data = EvaluateModelModule.run(
        scored_data=data_table,
        scored_data_to_compare=None)[0]
    metric_dict = scored_data.data.data_frame.iloc[0].to_dict()
    assert np.isclose(a=metric_dict['AUC'], b=0.0, rtol=1e-9)
    assert np.isclose(a=metric_dict['Accuracy'], b=0.6, rtol=1e-9)
    assert np.isclose(a=metric_dict['Precision'], b=1.0, rtol=1e-9)
    assert np.isclose(a=metric_dict['Recall'], b=0.6, rtol=1e-9)
    assert metric_dict['True Positive'] == 3
    assert metric_dict['True Negative'] == 0
    assert metric_dict['False Negative'] == 2
    assert metric_dict['False Positive'] == 0


def test_received_all_pos_data():
    data_table = _get_all_pos_binary_data()
    data_table.meta_data.label_column_name = 'Label'
    data_table.meta_data.score_column_names = _get_binary_score_columns()
    scored_data = EvaluateModelModule.run(scored_data=data_table, scored_data_to_compare=None)[0]
    metric_dict = scored_data.data.data_frame.iloc[0].to_dict()
    assert np.isclose(a=metric_dict['AUC'], b=0.0, rtol=1e-9)
    assert np.isclose(a=metric_dict['Accuracy'], b=1.0, rtol=1e-9)
    assert np.isclose(a=metric_dict['Precision'], b=1.0, rtol=1e-9)
    assert np.isclose(a=metric_dict['Recall'], b=1.0, rtol=1e-9)
    assert metric_dict['True Positive'] == 5
    assert metric_dict['True Negative'] == 0
    assert metric_dict['False Negative'] == 0
    assert metric_dict['False Positive'] == 0


def test_received_all_neg_data():
    data_table = _get_all_neg_binary_data()
    data_table.meta_data.label_column_name = 'Label'
    data_table.meta_data.score_column_names = _get_binary_score_columns()
    scored_data = EvaluateModelModule.run(scored_data=data_table, scored_data_to_compare=None)[0]
    metric_dict = scored_data.data.data_frame.iloc[0].to_dict()
    assert np.isclose(a=metric_dict['AUC'], b=0.0, rtol=1e-9)
    assert np.isclose(a=metric_dict['Accuracy'], b=1.0, rtol=1e-9)
    assert np.isclose(a=metric_dict['Precision'], b=0.0, rtol=1e-9)
    assert np.isclose(a=metric_dict['Recall'], b=0.0, rtol=1e-9)
    assert metric_dict['True Positive'] == 0
    assert metric_dict['True Negative'] == 5
    assert metric_dict['False Negative'] == 0
    assert metric_dict['False Positive'] == 0


def test_uncomparable_binary_scored_data():
    data_table = _get_illegal_extra_label_binary_scored_data()
    with pytest.raises(expected_exception=error_setting.NotExpectedLabelColumnError,
                       match=f'The label column "Label" is not expected in "Scored dataset"'):
        EvaluateModelModule.run(scored_data=data_table, scored_data_to_compare=None)


def test_encode_binary_label():
    binary_evaluator = BinaryClassificationEvaluator()
    data_frame = pd.DataFrame({
        'Label': [1, 0, 1, 0, 1],
        ScoreColumnConstants.ScoredProbabilitiesColumnName: [0.9, 0.1, 0.4, 0.6, 0.7],
        ScoreColumnConstants.ScoredLabelsColumnName: [1, 0, 0, 1, 1],
    })

    binary_evaluator.label_column_name = 'Label'
    binary_evaluator.prob_column_name = ScoreColumnConstants.ScoredProbabilitiesColumnName
    binary_evaluator.scored_label_column_name = ScoreColumnConstants.ScoredLabelsColumnName

    binary_evaluator._encode_label_column(data_frame)
    assert binary_evaluator.label_encoder.positive_label == 1
    assert binary_evaluator.label_encoder.negative_label == 0
    assert isinstance(binary_evaluator.label_encoder.positive_label, numbers.Integral)
    assert isinstance(binary_evaluator.label_encoder.negative_label, numbers.Integral)
