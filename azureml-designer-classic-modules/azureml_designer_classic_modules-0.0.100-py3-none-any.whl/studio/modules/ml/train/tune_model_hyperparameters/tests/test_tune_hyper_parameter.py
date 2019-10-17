from collections import namedtuple

import numpy as np
import pandas as pd
import pytest

import azureml.studio.common.error as error_setting
import azureml.studio.modules.ml.tests.mltest_utils as mltest_utils
from azureml.studio.common.datatable.data_table import DataTableColumnSelectionBuilder
from azureml.studio.core.utils.column_selection import ColumnKind
from azureml.studio.common.datatable.data_table import DataTable
from azureml.studio.modules.ml.common.base_learner import CreateLearnerMode
from azureml.studio.modules.ml.initialize_models.binary_classifier.boosted_decision_tree_biclassifier. \
    boosted_decision_tree_biclassifier import TwoClassBoostedDecisionTreeModule
from azureml.studio.modules.ml.initialize_models.multi_classifier.boosted_decision_tree_multiclassifier. \
    boosted_decision_tree_multiclassifier import MultiClassBoostedDecisionTreeModule
from azureml.studio.modules.ml.initialize_models.regressor.linear_regressor.linear_regressor import \
    CreateLinearRegressionModelSolutionMethod, LinearRegressionModule
from azureml.studio.modules.ml.train.tune_model_hyperparameters.tune_model_hyperparameters import \
    TuneModelHyperParametersModule, SweepMethods, \
    RegressionMetricType, BinaryClassificationMetricType
from azureml.studio.modules.python_language_modules.create_python_model.create_python_model import \
    CreatePythonModelModule, PYTHON_MODEL_SAMPLE

_default_tune_parameter = {
    'sweeping_mode': SweepMethods.RandomSweep,
    'binary_classification_metric': BinaryClassificationMetricType.Accuracy,
    'regression_metric': RegressionMetricType.CoefficientOfDetermination,
    'max_num_of_runs': 5,
    'random_seed': 42,
    'max_num_of_runs1': 5,
    'random_seed1': 42
}

TriFactors = namedtuple("TriFactors", "model data_sample column_selection")


@pytest.fixture()
def binary_classification_model():
    classifier, = TwoClassBoostedDecisionTreeModule.create_boosted_decision_tree_biclassifier(
        mode=CreateLearnerMode.SingleParameter)
    return classifier


@pytest.fixture()
def multiclass_classification_model():
    classifier, = MultiClassBoostedDecisionTreeModule.create_boosted_decision_tree_multiclassifier(
        mode=CreateLearnerMode.SingleParameter)
    return classifier


@pytest.fixture()
def regression_model():
    regressor, = LinearRegressionModule.create_linear_regressor(
        solution_method=CreateLinearRegressionModelSolutionMethod.OnlineGradientDescent,
        mode=CreateLearnerMode.SingleParameter)
    return regressor


@pytest.fixture()
def custom_model():
    model, = CreatePythonModelModule.run(python_stream_reader=PYTHON_MODEL_SAMPLE)
    return model


@pytest.fixture
def binary_classification_comb(binary_classification_model):
    return TriFactors(binary_classification_model, mltest_utils.binary_class_sample,
                      DataTableColumnSelectionBuilder().include_col_names(
                          mltest_utils.binary_class_sample.label_name).build())


@pytest.fixture
def multi_classification_comb(multiclass_classification_model):
    return TriFactors(multiclass_classification_model, mltest_utils.multi_class_sample,
                      DataTableColumnSelectionBuilder().include_col_names(
                          mltest_utils.multi_class_sample.label_name).build())


@pytest.fixture
def regression_comb(regression_model):
    return TriFactors(regression_model, mltest_utils.regression_sample,
                      DataTableColumnSelectionBuilder().include_col_names(
                          mltest_utils.regression_sample.label_name).build())


@pytest.fixture(params=["binary", "multi", "regression"])
def tri_factors(request, binary_classification_comb, multi_classification_comb, regression_comb):
    if request.param == "binary":
        return binary_classification_comb
    if request.param == "multi":
        return multi_classification_comb
    if request.param == "regression":
        return regression_comb


def test_tune_not_supported_model(custom_model):
    with pytest.raises(error_setting.LearnerTypesNotCompatibleError):
        TuneModelHyperParametersModule.run(
            predictor=custom_model,
            train_data=DataTable(mltest_utils.regression_sample.train_df),
            label_column_index_or_name=DataTableColumnSelectionBuilder().include_col_names(
                mltest_utils.regression_sample.label_name).build(),
            **_default_tune_parameter
        )


def test_train_none_learner():
    with pytest.raises(error_setting.NullOrEmptyError):
        TuneModelHyperParametersModule.run(
            predictor=None, train_data=DataTable(mltest_utils.regression_sample.train_df),
            label_column_index_or_name=DataTableColumnSelectionBuilder().include_col_names(
                mltest_utils.regression_sample.label_name).build(),
            **_default_tune_parameter)


def test_train_none_data_table(binary_classification_model):
    with pytest.raises(error_setting.TooFewRowsInDatasetError):
        TuneModelHyperParametersModule.run(
            predictor=binary_classification_model, train_data=DataTable(),
            label_column_index_or_name=DataTableColumnSelectionBuilder().include_col_names(
                mltest_utils.regression_sample.label_name).build(),
            **_default_tune_parameter)


def test_train_one_column_data_table(binary_classification_model):
    with pytest.raises(error_setting.TooFewColumnsInDatasetError):
        TuneModelHyperParametersModule.run(
            predictor=binary_classification_model, train_data=DataTable(
                pd.DataFrame(
                    mltest_utils.binary_class_sample.train_y, columns=[mltest_utils.binary_class_sample.label_name]
                )
            ),
            label_column_index_or_name=DataTableColumnSelectionBuilder().include_col_names(
                mltest_utils.regression_sample.label_name).build(),
            **_default_tune_parameter)


def test_train_zero_selected_column(tri_factors):
    model = tri_factors.model
    train_data = DataTable(tri_factors.data_sample.train_df)
    cs = DataTableColumnSelectionBuilder().include_col_kinds(ColumnKind.LABEL).build()
    with pytest.raises(error_setting.NotLabeledDatasetError, match='There is no label column in "Training dataset".'):
        TuneModelHyperParametersModule.run(
            predictor=model,
            train_data=train_data,
            label_column_index_or_name=cs,
            **_default_tune_parameter)


def test_train_all_nan_label(tri_factors):
    model = tri_factors.model
    data_sample = tri_factors.data_sample
    df = data_sample.train_x
    df[data_sample.label_name] = np.nan
    cs = tri_factors.column_selection
    train_data = DataTable(df)
    with pytest.raises(error_setting.LabelColumnDoesNotHaveLabeledPointsError):
        TuneModelHyperParametersModule.run(
            predictor=model,
            train_data=train_data,
            label_column_index_or_name=cs,
            **_default_tune_parameter
        )


def test_train_multiple_selected_column(tri_factors):
    model = tri_factors.model
    train_data = DataTable(tri_factors.data_sample.train_df)
    cs = DataTableColumnSelectionBuilder().include_col_indices('1-2').build()
    with pytest.raises(error_setting.MultipleLabelColumnsError,
                       match='Multiple label columns are specified in "Training dataset".'):
        TuneModelHyperParametersModule.run(
            predictor=model,
            train_data=train_data,
            label_column_index_or_name=cs,
            **_default_tune_parameter)


def test_regression_instances_less_than_fold(regression_comb):
    model = regression_comb.model
    train_data = DataTable(regression_comb.data_sample.train_df.head(2))
    cs = regression_comb.column_selection
    with pytest.raises(
            error_setting.NotExpectedLabelColumnError,
            match=f'The number of labeled instances should be greater '
                  f'than {TuneModelHyperParametersModule.DefaultNumberOfFolds}'):
        TuneModelHyperParametersModule.run(predictor=model, train_data=train_data, label_column_index_or_name=cs,
                                           **_default_tune_parameter)


def test_labeled_regression_instances_less_than_fold(regression_comb):
    model, data_sample, cs = regression_comb
    train_df = data_sample.train_df
    label_column_name = data_sample.label_name
    train_df[label_column_name] = np.nan
    train_df.loc[np.random.choice(train_df.shape[0], 2, replace=False), label_column_name] = (1, 3)
    train_data = DataTable(train_df)
    with pytest.raises(error_setting.NotExpectedLabelColumnError,
                       match=f'The number of labeled instances should be greater '
                             f'than {TuneModelHyperParametersModule.DefaultNumberOfFolds}'):
        TuneModelHyperParametersModule.run(predictor=model, train_data=train_data, label_column_index_or_name=cs,
                                           **_default_tune_parameter)


def test_classification_instances_less_than_fold(multi_classification_comb):
    model, data_sample, cs = multi_classification_comb
    train_df = data_sample.train_df.head(10)
    label_column_name = data_sample.label_name
    train_df[label_column_name] = ['a', 'b', 'c', np.nan, 'a', 'b', np.nan, 'c', 'a', 'b']
    train_data = DataTable(train_df)
    with pytest.raises(error_setting.NotExpectedLabelColumnError,
                       match=f'The number of members in each class should greater than '
                             f'{TuneModelHyperParametersModule.DefaultNumberOfFolds}.'):
        TuneModelHyperParametersModule.run(predictor=model, train_data=train_data, label_column_index_or_name=cs,
                                           **_default_tune_parameter)


def test_validation_none_data_table(binary_classification_comb):
    model, data_sample, cs = binary_classification_comb
    with pytest.raises(error_setting.TooFewRowsInDatasetError,
                       match='dataset "Optional validation dataset" is 0'):
        TuneModelHyperParametersModule.run(
            predictor=model, train_data=DataTable(data_sample.train_df),
            validation_data=DataTable(),
            label_column_index_or_name=cs,
            **_default_tune_parameter)


def test_validation_all_nan_label(tri_factors):
    model, data_sample, cs = tri_factors
    df = data_sample.train_x
    df[data_sample.label_name] = np.nan
    validation_data = DataTable(df)
    with pytest.raises(error_setting.LabelColumnDoesNotHaveLabeledPointsError):
        TuneModelHyperParametersModule.run(
            predictor=model,
            train_data=DataTable(data_sample.train_df),
            validation_data=validation_data,
            label_column_index_or_name=cs,
            **_default_tune_parameter
        )


def test_validation_missing_columns_not_comparable(binary_classification_comb):
    model, data_sample, cs = binary_classification_comb
    train_data = DataTable(data_sample.train_df)
    validation_df = data_sample.train_df
    validation_df = validation_df.iloc[:, 2:]
    with pytest.raises(error_setting.ColumnNotFoundError):
        TuneModelHyperParametersModule.run(
            predictor=model,
            train_data=train_data,
            validation_data=DataTable(validation_df),
            label_column_index_or_name=cs,
            **_default_tune_parameter)


@pytest.mark.parametrize('new_type', ['str', 'category'])
def test_validation_data_type_not_comparable(binary_classification_comb, new_type):
    model, data_sample, cs = binary_classification_comb
    train_data = DataTable(data_sample.train_df)
    validation_df = data_sample.train_df
    validation_df.iloc[:, 0] = validation_df.iloc[:, 0].astype(new_type)
    with pytest.raises(error_setting.NotCompatibleColumnTypesError):
        TuneModelHyperParametersModule.run(
            predictor=model,
            train_data=train_data,
            validation_data=DataTable(validation_df),
            label_column_index_or_name=cs,
            **_default_tune_parameter
        )


def test_validation_binary_label_not_comparable(binary_classification_comb):
    model, data_sample, cs = binary_classification_comb
    train_data = DataTable(data_sample.train_df)
    validation_df = data_sample.train_df
    label_column_name = data_sample.label_name
    validation_df.loc[validation_df[label_column_name] == 0, label_column_name] = 4
    with pytest.raises(error_setting.NotExpectedLabelColumnError,
                       match='Validation label column is not consistent with the training label column.'):
        TuneModelHyperParametersModule.run(
            predictor=model,
            train_data=train_data,
            validation_data=DataTable(validation_df),
            label_column_index_or_name=cs,
            **_default_tune_parameter)


def test_validation_multiclass_label_not_comparable(multi_classification_comb):
    model, data_sample, cs = multi_classification_comb
    train_data = DataTable(data_sample.train_df)
    validation_df = data_sample.train_df
    label_column_name = data_sample.label_name
    validation_df[label_column_name] = validation_df[label_column_name] + 1
    with pytest.raises(error_setting.NotExpectedLabelColumnError,
                       match='Validation label column is not consistent with the training label column.'):
        TuneModelHyperParametersModule.run(
            predictor=model,
            train_data=train_data,
            validation_data=DataTable(validation_df),
            label_column_index_or_name=cs,
            **_default_tune_parameter)


@pytest.mark.parametrize('metric', [BinaryClassificationMetricType.AverageLogLoss,
                                    BinaryClassificationMetricType.AUC,
                                    BinaryClassificationMetricType.Accuracy,
                                    BinaryClassificationMetricType.FScore,
                                    BinaryClassificationMetricType.Recall,
                                    BinaryClassificationMetricType.Precision])
def test_binary_metric_work(binary_classification_comb, metric):
    model, data_sample, cs = binary_classification_comb
    train_data = DataTable(data_sample.train_df)
    validation_df = data_sample.train_df
    other_parameter = _default_tune_parameter
    other_parameter.update(binary_classification_metric=metric)
    res, model = TuneModelHyperParametersModule.run(
        predictor=model,
        train_data=train_data,
        validation_data=DataTable(validation_df),
        label_column_index_or_name=cs,
        **other_parameter
    )
    assert res.number_of_columns == 11


@pytest.mark.parametrize('metric', [RegressionMetricType.CoefficientOfDetermination,
                                    RegressionMetricType.RelativeSquaredError,
                                    RegressionMetricType.RelativeAbsoluteError,
                                    RegressionMetricType.RootMeanSquaredError,
                                    RegressionMetricType.MeanAbsoluteError])
def test_regression_metric_work(regression_comb, metric):
    model, data_sample, cs = regression_comb
    train_data = DataTable(data_sample.train_df)
    validation_df = data_sample.train_df
    other_parameter = _default_tune_parameter
    other_parameter.update(regression_metric=metric)
    res, model = TuneModelHyperParametersModule.run(
        predictor=model,
        train_data=train_data,
        validation_data=DataTable(validation_df),
        label_column_index_or_name=cs,
        **other_parameter
    )
    assert res


def test_number_of_runs_work(tri_factors):
    model, data_sample, cs = tri_factors
    train_data = DataTable(data_sample.train_df)
    other_parameter = _default_tune_parameter
    max_number_of_runs = np.random.randint(1, 10)
    other_parameter.update(max_num_of_runs=max_number_of_runs)
    res, _ = TuneModelHyperParametersModule.run(
        predictor=model,
        train_data=train_data,
        label_column_index_or_name=cs,
        **other_parameter
    )
    assert res.number_of_rows == max_number_of_runs
