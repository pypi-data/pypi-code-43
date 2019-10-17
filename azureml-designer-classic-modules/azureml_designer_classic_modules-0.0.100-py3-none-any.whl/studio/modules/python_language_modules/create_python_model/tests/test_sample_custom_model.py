import os
import pandas as pd
import numpy as np
import pytest

from azureml.studio.common.datatable.data_table import DataTableColumnSelectionBuilder
from azureml.studio.common.datatable.data_table import DataTable
from azureml.studio.common.io.pickle_utils import read_with_pickle_from_file
from azureml.studio.modules.ml.score.score_generic_module.score_generic_module import ScoreModelModule
from azureml.studio.modules.ml.train.train_generic_model.train_generic_model import TrainModelModule
from azureml.studio.modules.python_language_modules.create_python_model.create_python_model import \
    CreatePythonModelModule, PYTHON_MODEL_SAMPLE
from azureml.studio.modules.python_language_modules.create_python_model.tests.test_custom_model_binary_classification\
    import EXPECT_FOLDER_NAME, INPUT_FOLDER_NAME, trained_prefix, untrained_prefix

sample_python_script = PYTHON_MODEL_SAMPLE

binary_classification_file_name = 'binary_classification.ilearner'


def script_directory():
    return os.path.dirname(os.path.abspath(__file__))


def binary_classification_training_data():
    df = pd.DataFrame()
    df['col0'] = [1, 2, 3, 4]
    df['col1'] = [1, 1, 0, 0]
    return DataTable(df)


def binary_classification_predict_data():
    df = pd.DataFrame()
    df['col0'] = [1, 2, 3, 4]
    return DataTable(df)


def binary_classification_expect_predict_result():
    return pd.DataFrame({'col0': [1, 2, 3, 4], 'Scored Labels': [1, 0, 0, 0]})


def label_column():
    return DataTableColumnSelectionBuilder().include_col_names('col1').build()


def check_computed_model(computed_model, expect_file_name):
    expect_full_file_path = os.path.join(script_directory(), EXPECT_FOLDER_NAME, expect_file_name)
    expect_model = read_with_pickle_from_file(expect_full_file_path)
    for expect_key, expect_value in expect_model.custom_model.model.__dict__.items():
        compute_value = computed_model.custom_model.model.__dict__.get(expect_key)
        if isinstance(expect_value, np.ndarray):
            np.testing.assert_array_almost_equal(expect_value, compute_value)
        elif isinstance(expect_value, str):
            assert expect_value == compute_value
        elif expect_value is None:
            assert expect_value == compute_value
        else:
            assert expect_value == pytest.approx(compute_value)


def read_input_model(input_file_name):
    input_full_file_path = os.path.join(script_directory(), INPUT_FOLDER_NAME, input_file_name)
    return read_with_pickle_from_file(input_full_file_path)


def test_init_model_binary_classification():
    init_model = CreatePythonModelModule.run(
        python_stream_reader=sample_python_script)[0]
    expect_file_name = untrained_prefix + binary_classification_file_name
    check_computed_model(init_model, expect_file_name)


def test_train_model_binary_classification():
    input_file_name = untrained_prefix + binary_classification_file_name
    untrained_model = read_input_model(input_file_name)
    training_data = binary_classification_training_data()
    trained_model = TrainModelModule.run(
        learner=untrained_model,
        training_data=binary_classification_training_data(),
        label_column_index_or_name=label_column()
    )[0]
    assert trained_model.is_trained
    expect_feature_column_names = training_data.column_names
    label_column_index = label_column().select_column_indexes(training_data)[0]
    del expect_feature_column_names[label_column_index]

    assert trained_model.custom_model.feature_column_names == expect_feature_column_names
    expect_file_name = trained_prefix + binary_classification_file_name
    check_computed_model(trained_model, expect_file_name)


def test_score_model_binary_classification():
    input_file_name = trained_prefix + binary_classification_file_name
    trained_model = read_input_model(input_file_name)
    scored_dt = ScoreModelModule.run(
        learner=trained_model,
        test_data=binary_classification_predict_data(),
        append_or_result_only=True
    )[0]
    assert scored_dt.data_frame.equals(binary_classification_expect_predict_result())
