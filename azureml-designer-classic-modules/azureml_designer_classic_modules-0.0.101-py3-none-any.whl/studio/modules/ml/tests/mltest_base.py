import copy
import os
from abc import ABC

import numpy as np
import pandas as pd
import pytest
from azureml.studio.core.utils.column_selection import ColumnKind

import azureml.studio.common.error as error_setting
import azureml.studio.modules.ml.tests.mltest_utils as mltest_utils
from azureml.studio.common.datatable.data_table import DataTable
from azureml.studio.common.datatable.data_table import DataTableColumnSelectionBuilder
from azureml.studio.common.parameter_range import Sweepable, ParameterRangeSettings
from azureml.studio.modulehost.attributes import ReleaseState
from azureml.studio.modulehost.handler.sidecar_files import SideCarFileBundle
from azureml.studio.modules.datatransform.partition_and_sample.partition_and_sample \
    import SampleMethods, PartitionMethods, TrueFalseType, PartitionAndSampleModule
from azureml.studio.modules.ml.common.base_learner import CreateLearnerMode
from azureml.studio.modules.ml.common.constants import ScoreColumnConstants
from azureml.studio.modules.ml.common.learner_parameter_sweeper import SweepMethods, BinaryClassificationMetricType, \
    RegressionMetricType
from azureml.studio.modules.ml.common.ml_utils import TaskType
from azureml.studio.modules.ml.evaluate.cross_validate_module.cross_validate_module import CrossValidateModelModule
from azureml.studio.modules.ml.evaluate.evaluate_generic_module.evaluate_generic_module import EvaluateModelModule
from azureml.studio.modules.ml.evaluate.evaluate_generic_module.evaluate_generic_module import evaluate_generic
from azureml.studio.modules.ml.initialize_models.multi_classifier.one_vs_all_multiclassifier. \
    one_vs_all_multiclassifier import OneVsAllMulticlassModule
from azureml.studio.modules.ml.score.score_generic_module.score_generic_module import ScoreModelModule
from azureml.studio.modules.ml.train.train_generic_model.train_generic_model import TrainModelModule
from azureml.studio.modules.ml.train.tune_model_hyperparameters.tune_model_hyperparameters import \
    TuneModelHyperParametersModule

_TaskMetricName = {
    TaskType.BinaryClassification: "F1",
    TaskType.MultiClassification: "Overall_Accuracy",
    TaskType.Regression: "Mean_Absolute_Error"
}


class CommonBase(ABC):
    entry_class = ScoreModelModule  # sub class must change this to Initialize Model Module entry
    model_class = None
    default_single_parameter = dict()
    default_range_parameter = dict()
    performance_assert_function = mltest_utils.assert_less
    performance_assert_threshold = 1.0
    personal_setting = dict()
    label_column_name = 'label'
    train_sample = mltest_utils.regression_sample
    label_kind_column_selection = DataTableColumnSelectionBuilder().include_col_kinds(ColumnKind.LABEL).build()
    multiple_label_columns_selection = DataTableColumnSelectionBuilder().include_col_indices('1-2').build()

    @property
    def column_selection(self):
        csb = DataTableColumnSelectionBuilder()
        return csb.include_col_names(self.label_column_name).build()

    @classmethod
    def _get_single_parameter_dict(cls):
        dp = dict()
        dp.update(cls.default_single_parameter)
        dp.update({'mode': CreateLearnerMode.SingleParameter})
        return dp

    @classmethod
    def _get_range_parameter_dict(cls):
        dp = dict()
        dp.update(cls.default_range_parameter)
        dp.update({'mode': CreateLearnerMode.ParameterRange})
        return dp

    def _init_model(self, **kwargs):
        param = self._get_single_parameter_dict()
        param.update(kwargs)
        out = self.entry_class.run(**param)
        clf = out[0]
        return clf

    def _init_range_model(self, **kwargs):
        param = self._get_range_parameter_dict()
        param.update(kwargs)
        clf, = self.entry_class.run(**param)
        return clf

    def _get_trained_model(self):
        clf = self._init_model()
        clf = TrainModelModule.run(learner=clf, training_data=DataTable(self.train_sample.train_df),
                                   label_column_index_or_name=self.column_selection)[0]
        return clf

    def test_create_model(self, **kwargs):
        dp = self._get_single_parameter_dict()
        dp.update(**kwargs)
        out = self.entry_class.run(**dp)
        assert isinstance(out, tuple)
        assert len(out) == 1
        assert isinstance(out[0], self.model_class)
        return out[0]

    def test_train_none_learner(self):
        with pytest.raises(error_setting.NullOrEmptyError):
            TrainModelModule.run(learner=None,
                                 training_data=DataTable(self.train_sample.train_df),
                                 label_column_index_or_name=self.column_selection)

    def test_train_none_data_table(self):
        clf = self._init_model()
        with pytest.raises(error_setting.TooFewRowsInDatasetError):
            TrainModelModule.run(learner=clf,
                                 training_data=DataTable(pd.DataFrame()),
                                 label_column_index_or_name=self.column_selection)

    def test_train_one_column_data_table(self):
        clf = self._init_model()
        with pytest.raises(error_setting.TooFewColumnsInDatasetError):
            TrainModelModule.run(learner=clf,
                                 training_data=DataTable(
                                     pd.DataFrame(self.train_sample.train_y,
                                                  columns=[self.label_column_name])),
                                 label_column_index_or_name=self.column_selection)

    def test_train_nan_label_column_data_table(self):
        clf = self._init_model()
        df = self.train_sample.train_x
        df[self.label_column_name] = np.nan
        with pytest.raises(error_setting.LabelColumnDoesNotHaveLabeledPointsError):
            TrainModelModule.run(learner=clf,
                                 training_data=DataTable(df),
                                 label_column_index_or_name=self.column_selection)

    def test_train_zero_selected_column(self):
        clf = self._init_model()
        df = self.train_sample.train_x
        with pytest.raises(error_setting.NotLabeledDatasetError,
                           match='There is no label column in "Dataset".'):
            TrainModelModule.run(learner=clf,
                                 training_data=DataTable(df),
                                 label_column_index_or_name=self.label_kind_column_selection)

    def test_train_multiple_selected_column(self):
        clf = self._init_model()
        df = self.train_sample.train_x
        with pytest.raises(error_setting.MultipleLabelColumnsError,
                           match='Multiple label columns are specified in "Dataset".'):
            TrainModelModule.run(learner=clf,
                                 training_data=DataTable(df),
                                 label_column_index_or_name=self.multiple_label_columns_selection)

    # test score model
    def test_get_untrained_error(self):
        clf = self._init_model()
        with pytest.raises(error_setting.UntrainedModelError):
            ScoreModelModule.run(
                learner=clf,
                test_data=DataTable(self.train_sample.train_x),
                append_or_result_only=True)

    def test_get_empty_test_data_error(self):
        model = self._get_trained_model()
        model.label_column_name = self.label_column_name
        with pytest.raises(error_setting.TooFewRowsInDatasetError):
            ScoreModelModule.run(
                learner=model,
                test_data=DataTable(pd.DataFrame()),
                append_or_result_only=True)

    def test_score_success(self):
        model = self._get_trained_model()
        model.label_column_name = self.label_column_name
        result = ScoreModelModule.run(
            learner=model,
            test_data=DataTable(self.train_sample.train_df),
            append_or_result_only=True)

        assert isinstance(result, tuple)
        assert len(result) == 1
        assert isinstance(result[0], DataTable)
        assert 'Scored Labels' in result[0].column_names
        assert result[0].number_of_rows == self.train_sample.train_df.shape[0]

    def test_score_scored_data_success(self):
        model = self._get_trained_model()
        model.label_column_name = self.label_column_name
        scored_data = ScoreModelModule.run(
            learner=model,
            test_data=DataTable(self.train_sample.train_df),
            append_or_result_only=True)[0]
        scored_data_ref = copy.deepcopy(scored_data)
        score_column_names = [x for x in scored_data.column_names if
                              x == ScoreColumnConstants.ScoredLabelsColumnName or x.startswith(
                                  ScoreColumnConstants.ScoredProbabilitiesMulticlassColumnNamePattern)]

        for name in score_column_names:
            scored_data.set_column(name, pd.Series([np.nan] * scored_data.number_of_rows))
        rescored_data = ScoreModelModule.run(
            learner=model,
            test_data=scored_data,
            append_or_result_only=True)[0]
        assert all(rescored_data.data_frame[score_column_names].notna())
        mltest_utils.assert_data_table_equals(scored_data_ref, rescored_data)

    def test_required_feature_not_found(self):
        model = self._get_trained_model()
        missing_feature_df = self.train_sample.train_df.iloc[:, 1:]
        with pytest.raises(error_setting.MissingFeaturesError):
            ScoreModelModule.run(
                learner=model,
                test_data=DataTable(missing_feature_df),
                append_or_result_only=True)

    # test evaluate model
    def test_evaluate_non_label_data(self):
        model = self._get_trained_model()
        model.label_column_name = self.label_column_name
        result = ScoreModelModule.run(
            learner=model,
            test_data=DataTable(self.train_sample.train_x),
            append_or_result_only=True)
        with pytest.raises(error_setting.NotLabeledDatasetError):
            EvaluateModelModule.run(
                scored_data=result[0],
                scored_data_to_compare=None)

    def test_check_col_type_compatible(self):
        data_type = {'f0': np.int16, 'f1': np.float64, 'f2': str, 'label': np.int16}
        data_path = os.path.join(mltest_utils.input_dataset_base_library(), 'check_col_type_compatible')
        train_df = pd.read_csv(os.path.join(data_path, 'train.csv'), dtype=data_type)
        test_df = pd.read_csv(os.path.join(data_path, 'test_negative.csv'))
        clf = self._init_model()
        TrainModelModule.run(learner=clf,
                             training_data=DataTable(train_df),
                             label_column_index_or_name=DataTableColumnSelectionBuilder().include_col_names(
                                 'label').build()
                             )
        with pytest.raises(error_setting.NotCompatibleColumnTypesError, match="between train"):
            ScoreModelModule.run(
                learner=clf,
                test_data=DataTable(test_df),
                append_or_result_only=True)

    @pytest.mark.parametrize(
        'sweeping_mode', [SweepMethods.RandomSweep,
                          # todo :reduce search space. Too large search space, sweep EntireGrid would be extremely slow.
                          # SweepMethods.EntireGrid
                          ]
    )
    @pytest.mark.parametrize('cross_validation', [
        True, False
    ])
    def test_co_work_with_tune_hyper(self, sweeping_mode, cross_validation):
        clf = self._init_range_model()
        test_data = DataTable(self.train_sample.train_df)
        if cross_validation:
            train_data = DataTable(self.train_sample.train_df)
            validation_data = None
        else:
            train_df, valid_df = self.train_sample.split_data
            train_data = DataTable(train_df)
            validation_data = DataTable(valid_df)
        report, model = TuneModelHyperParametersModule.run(
            predictor=clf, train_data=train_data, validation_data=validation_data,
            label_column_index_or_name=self.column_selection,
            sweeping_mode=sweeping_mode,
            binary_classification_metric=BinaryClassificationMetricType.Accuracy,
            regression_metric=RegressionMetricType.CoefficientOfDetermination,
            max_num_of_runs=5, random_seed=42, max_num_of_runs1=5,
            random_seed1=42)
        assert isinstance(model, self.model_class)
        _check_report_columns(report, self.entry_class, self.default_range_parameter)
        scored_data, = ScoreModelModule.run(learner=model, test_data=test_data, append_or_result_only=False)
        evaluate_result = evaluate_generic(scored_data=scored_data, scored_data_to_compare=None)
        metric_value = _get_metric_value(evaluate_result, metric_name=_TaskMetricName[model.task_type])
        self.performance_assert_function(metric_value, self.performance_assert_threshold)

    # bug 474888: score module concatenate dataframes with different index.
    def test_score_discontinuous_index(self):
        learner = self._get_trained_model()
        data_frame = self.train_sample.train_df
        # select subset of data
        random_index = np.random.choice(list(data_frame.index), data_frame.shape[0] // 2)
        random_index.sort()
        random_index = np.unique(random_index)
        data_frame = data_frame.loc[random_index]
        data_table = DataTable(data_frame)

        # score discontinuous index data
        scored_data = ScoreModelModule.run(learner=learner, test_data=data_table, append_or_result_only=True)[0]
        assert scored_data.number_of_rows == data_table.number_of_rows


class RegressionCommonCase(CommonBase):
    label_column_name = 'label'
    train_sample = mltest_utils.regression_sample
    performance_assert_function = mltest_utils.assert_less

    def test_train_on_non_numeric_label(self):
        wrong_sample = mltest_utils.multi_class_sample
        train_df = wrong_sample.train_df
        train_df['flower_type'] = train_df['flower_type'].apply(lambda x: str(x) + '1')
        model = self._init_model()
        cs = DataTableColumnSelectionBuilder().include_col_names('flower_type').build()
        with pytest.raises(error_setting.InvalidTrainingDatasetError):
            TrainModelModule.run(learner=model,
                                 training_data=DataTable(train_df),
                                 label_column_index_or_name=cs)

    def test_train_success(self):
        clf = self._init_model()
        df = self.train_sample.train_df
        result = TrainModelModule.run(learner=clf,
                                      training_data=DataTable(df),
                                      label_column_index_or_name=self.column_selection)
        assert isinstance(result, tuple)
        assert len(result) == 1
        assert isinstance(result[0], self.model_class)
        assert result[0].is_trained
        model = result[0]
        result = mltest_utils.get_ase(model)
        self.performance_assert_function(result, self.performance_assert_threshold)

    def test_evaluate_success(self):
        model = self._get_trained_model()
        model.label_column_name = 'label'
        scored_data = ScoreModelModule.run(
            learner=model,
            test_data=DataTable(self.train_sample.train_df),
            append_or_result_only=True)[0]
        result = EvaluateModelModule.run(
            scored_data=scored_data,
            scored_data_to_compare=None)
        assert isinstance(result, tuple)
        assert len(result) == 1
        evaluate_data = result[0]
        assert isinstance(evaluate_data, DataTable)
        assert 'Mean_Absolute_Error' in evaluate_data.column_names
        assert 'Root_Mean_Squared_Error' in evaluate_data.column_names
        assert 'Relative_Squared_Error' in evaluate_data.column_names
        assert 'Relative_Absolute_Error' in evaluate_data.column_names
        assert 'Coefficient_of_Determination' in evaluate_data.column_names

    def test_cross_validate_error(self):
        clf = self._init_model()
        df = self.train_sample.train_df.head()
        # Default n_partition value (10) because not previously partitioned, which is greater than row num (5) of df
        # Trigger TooFewRowsInDatasetError as a result
        with pytest.raises(error_setting.TooFewRowsInDatasetError,
                           match='Number of rows in input dataset "num_samples" is 5, less than allowed'):
            CrossValidateModelModule.run(
                learner=clf,
                training_data=DataTable(df),
                label_column_index_or_name=self.column_selection,
                random_seed=0
            )

    def test_cross_validate_success(self):
        clf = self._init_model()
        df = self.train_sample.train_df.head(8)
        # n_partition value is set to 8 with previously partitioned
        # pylint: disable=no-value-for-parameter
        nfold_partition_dt = PartitionAndSampleModule.run(
            table=DataTable(df),
            method=SampleMethods.NFoldSplit,
            with_replacement=False,
            random_flag=False,
            seed=123,
            partition_method=PartitionMethods.EvenSizePartitioner,
            num_partitions=8,
            stratify_flag1=TrueFalseType.FALSE
        )[0]
        score_results, eval_results = CrossValidateModelModule.run(
            learner=clf,
            training_data=nfold_partition_dt,
            label_column_index_or_name=self.column_selection,
            random_seed=0
        )
        assert isinstance(score_results, DataTable)
        assert 'Scored Labels' in score_results.column_names
        assert 'Fold Number' in score_results.column_names
        assert score_results.number_of_rows == self.train_sample.train_df.shape[0]
        assert isinstance(eval_results, DataTable)
        assert 'Fold Number' in eval_results.column_names
        assert 'Number of examples in fold' in eval_results.column_names
        assert 'Mean_Absolute_Error' in eval_results.column_names
        assert 'Root_Mean_Squared_Error' in eval_results.column_names
        assert 'Relative_Squared_Error' in eval_results.column_names
        assert 'Relative_Absolute_Error' in eval_results.column_names
        assert 'Coefficient_of_Determination' in eval_results.column_names

    def test_tse(self):
        clf = self._init_model()
        df = self.train_sample.train_df
        model = TrainModelModule.run(learner=clf,
                                     training_data=DataTable(df),
                                     label_column_index_or_name=self.column_selection)[0]
        scored_data = ScoreModelModule.run(
            learner=model,
            test_data=DataTable(self.train_sample.train_df),
            append_or_result_only=True)[0]
        result = EvaluateModelModule.run(
            scored_data=scored_data,
            scored_data_to_compare=None)[0]
        self.performance_assert_function(result.data_frame['Mean_Absolute_Error'].tolist()[0],
                                         self.performance_assert_threshold)

    def test_as_base_model_of_one_vs_all_classifier(self):
        binary_model = self._init_model()
        with pytest.raises(error_setting.InvalidLearnerError, match=f'has invalid type "{self.model_class.__name__}"'):
            _ = OneVsAllMulticlassModule.run(learner=binary_model)


class MultiClassCommonCase(CommonBase):
    label_column_name = 'flower_type'
    train_sample = mltest_utils.multi_class_sample
    performance_assert_function = mltest_utils.assert_greater

    def test_train_success(self):
        clf = self._init_model()
        df = self.train_sample.train_df
        result = TrainModelModule.run(learner=clf,
                                      training_data=DataTable(df),
                                      label_column_index_or_name=self.column_selection)
        assert isinstance(result, tuple)
        assert len(result) == 1
        assert isinstance(result[0], self.model_class)
        assert result[0].is_trained
        model = result[0]
        result = mltest_utils.get_accuracy(model)
        self.performance_assert_function(result, self.performance_assert_threshold)

    def test_evaluate_success(self):
        model = self._get_trained_model()
        model.label_column_name = 'flower_type'
        scored_data = ScoreModelModule.run(
            learner=model,
            test_data=DataTable(self.train_sample.train_df),
            append_or_result_only=True)[0]
        result = EvaluateModelModule.run(
            scored_data=scored_data,
            scored_data_to_compare=None)
        assert isinstance(result, tuple)
        assert len(result) == 1
        evaluate_data = result[0]
        assert isinstance(evaluate_data, DataTable)
        assert 'Overall_Accuracy' in evaluate_data.column_names
        assert 'Micro_Precision' in evaluate_data.column_names
        assert 'Macro_Precision' in evaluate_data.column_names
        assert 'Micro_Recall' in evaluate_data.column_names
        assert 'Macro_Recall' in evaluate_data.column_names

    def test_cross_validate_success(self):
        clf = self._init_model()
        df = self.train_sample.train_df
        score_results, eval_results = CrossValidateModelModule.run(
            learner=clf,
            training_data=DataTable(df),
            label_column_index_or_name=self.column_selection,
            random_seed=0
        )
        assert isinstance(score_results, DataTable)
        assert 'Scored Labels' in score_results.column_names
        assert 'Fold Number' in score_results.column_names
        assert score_results.number_of_rows == self.train_sample.train_df.shape[0]
        assert isinstance(eval_results, DataTable)
        assert 'Fold Number' in eval_results.column_names
        assert 'Number of examples in fold' in eval_results.column_names
        assert 'Overall_Accuracy' in eval_results.column_names
        assert 'Micro_Precision' in eval_results.column_names
        assert 'Macro_Precision' in eval_results.column_names
        assert 'Micro_Recall' in eval_results.column_names
        assert 'Macro_Recall' in eval_results.column_names

    def test_tse(self):
        clf = self._init_model()
        df = self.train_sample.train_df
        model = TrainModelModule.run(learner=clf,
                                     training_data=DataTable(df),
                                     label_column_index_or_name=self.column_selection)[0]
        scored_data = ScoreModelModule.run(
            learner=model,
            test_data=DataTable(mltest_utils.multi_class_sample.train_df),
            append_or_result_only=True)[0]
        result = EvaluateModelModule.run(
            scored_data=scored_data,
            scored_data_to_compare=None)[0]
        self.performance_assert_function(result.data_frame['Overall_Accuracy'].tolist()[0],
                                         self.performance_assert_threshold)

    def test_int_category_label_with_None(self):
        train_df = pd.DataFrame({'a': [1, 2, 3, 4, 1], 'label': [1, 2, 3, 4, None]}, dtype='category')
        test_df = pd.DataFrame({'a': [1, 2, 3, 4, None, 5], 'label': [1, 2, 3, 4, None, 1]}, dtype='category')
        clf = self._init_model()
        column_selection = DataTableColumnSelectionBuilder().include_col_names('label').build()
        trained_learner = TrainModelModule.run(learner=clf,
                                               training_data=DataTable(train_df),
                                               label_column_index_or_name=column_selection)[0]
        scored_date = \
            ScoreModelModule.run(learner=trained_learner, test_data=DataTable(test_df), append_or_result_only=True)[0]
        assert scored_date.number_of_rows == 6
        EvaluateModelModule.run(scored_data=scored_date, scored_data_to_compare=None)

    def test_int_category_label_with_nan(self):
        train_df = pd.DataFrame({'a': [1, 2, 3, 4, 1], 'label': [1, 2, 3, 4, np.nan]}, dtype='category')
        test_df = pd.DataFrame({'a': [1, 2, 3, 4, None, 5], 'label': [1, 2, 3, 4, np.nan, 1]}, dtype='category')
        clf = self._init_model()
        column_selection = DataTableColumnSelectionBuilder().include_col_names('label').build()
        trained_learner = TrainModelModule.run(learner=clf,
                                               training_data=DataTable(train_df),
                                               label_column_index_or_name=column_selection)[0]
        scored_date = \
            ScoreModelModule.run(learner=trained_learner, test_data=DataTable(test_df), append_or_result_only=True)[0]
        assert scored_date.number_of_rows == 6
        EvaluateModelModule.run(scored_data=scored_date, scored_data_to_compare=None)

    def test_str_category_label_with_None(self):
        train_df = pd.DataFrame({'a': ['a', 'b', 'c', 'a', 'b'], 'label': ['a', 'b', 'c', None, 'b']}, dtype='category')
        test_df = pd.DataFrame({'a': ['a', 'b', 'c'], 'label': ['a', 'b', None]}, dtype='category')
        clf = self._init_model()
        column_selection = DataTableColumnSelectionBuilder().include_col_names('label').build()
        trained_learner = TrainModelModule.run(learner=clf,
                                               training_data=DataTable(train_df),
                                               label_column_index_or_name=column_selection)[0]
        scored_date = \
            ScoreModelModule.run(learner=trained_learner, test_data=DataTable(test_df), append_or_result_only=True)[0]
        assert scored_date.number_of_rows == 3
        EvaluateModelModule.run(scored_data=scored_date, scored_data_to_compare=None)

    def test_str_category_label_with_nan(self):
        train_df = pd.DataFrame({'a': ['a', 'b', 'c', 'a', 'b'], 'label': ['a', 'b', 'c', np.nan, 'b']},
                                dtype='category')
        test_df = pd.DataFrame({'a': ['a', 'b', 'c'], 'label': ['a', 'b', np.nan]}, dtype='category')
        clf = self._init_model()
        column_selection = DataTableColumnSelectionBuilder().include_col_names('label').build()
        trained_learner = TrainModelModule.run(learner=clf,
                                               training_data=DataTable(train_df),
                                               label_column_index_or_name=column_selection)[0]
        scored_date = \
            ScoreModelModule.run(learner=trained_learner, test_data=DataTable(test_df), append_or_result_only=True)[0]
        assert scored_date.number_of_rows == 3
        EvaluateModelModule.run(scored_data=scored_date, scored_data_to_compare=None)

    @pytest.fixture()
    def input_data_table_multi_types(self):
        df = pd.DataFrame()
        df['int'] = [1, 10, np.nan]
        df['float'] = [1.6, np.nan, 1]
        df['string'] = [np.nan, '3', '1']
        df['bool'] = [True, np.nan, False]
        df['category'] = pd.Series([2, 1, 3]).astype('category')
        df['datetime'] = pd.to_datetime(
            arg=pd.Series(['20190101', '20190103', np.nan]), format='%Y%m%d', errors='coerce')
        df['timespan'] = pd.to_timedelta(
            arg=pd.Series([5, 10, np.nan]), unit='days', errors='coerce')
        df['nan'] = [np.nan, np.nan, np.nan]
        df['label'] = [1, 3, 1]
        return DataTable(df)

    def test_mix_type_training_data(self, input_data_table_multi_types):
        clf = self._init_model()
        column_selection = DataTableColumnSelectionBuilder().include_col_names('label').build()
        trained_learner = TrainModelModule.run(learner=clf,
                                               training_data=input_data_table_multi_types,
                                               label_column_index_or_name=column_selection)[0]
        scored_date = \
            ScoreModelModule.run(learner=trained_learner, test_data=input_data_table_multi_types,
                                 append_or_result_only=True)[0]
        assert scored_date.number_of_rows == 3
        EvaluateModelModule.run(scored_data=scored_date, scored_data_to_compare=None)

    @pytest.fixture()
    def input_data_table_multi_category_types(self):
        df = pd.DataFrame()
        df['int'] = pd.Series([1, 10, np.nan], dtype='category')
        df['float'] = pd.Series([1.6, np.nan, 1], dtype='category')
        df['string'] = pd.Series([np.nan, '3', '1'], dtype='category')
        df['bool'] = pd.Series([True, np.nan, False], dtype='category')
        df['category'] = pd.Series([2, 1, 3]).astype('category')
        df['datetime'] = pd.to_datetime(
            arg=pd.Series(['20190101', '20190103', np.nan]), format='%Y%m%d', errors='coerce')
        df['timespan'] = pd.to_timedelta(
            arg=pd.Series([5, 10, np.nan]), unit='days', errors='coerce')
        df['nan'] = [np.nan, np.nan, np.nan]
        df['label'] = [1, 2, 1]
        return DataTable(df)

    def test_mix_category_type_training_data(self, input_data_table_multi_category_types):
        clf = self._init_model()
        column_selection = DataTableColumnSelectionBuilder().include_col_names('label').build()
        trained_learner = TrainModelModule.run(learner=clf,
                                               training_data=input_data_table_multi_category_types,
                                               label_column_index_or_name=column_selection)[0]
        scored_date = \
            ScoreModelModule.run(learner=trained_learner, test_data=input_data_table_multi_category_types,
                                 append_or_result_only=True)[0]
        assert scored_date.number_of_rows == 3
        EvaluateModelModule.run(scored_data=scored_date, scored_data_to_compare=None)

    def test_training_on_one_class_data(self):
        clf = self._init_model()
        column_selection = DataTableColumnSelectionBuilder().include_col_names('label').build()
        one_class_training_data = DataTable(pd.DataFrame({'f1': [1, 2, 3], 'label': [1, 1, 1]}))
        with pytest.raises(expected_exception=error_setting.InvalidTrainingDatasetError,
                           match='The number of label classes should > 1'):
            _ = TrainModelModule.run(learner=clf,
                                     training_data=one_class_training_data,
                                     label_column_index_or_name=column_selection)[0]

    @pytest.mark.parametrize(
        'is_category',
        [True,
         False
         ]
    )
    def test_unique_values_data(self, is_category):
        data_path = os.path.join(mltest_utils.input_dataset_base_library(), 'unique_values_dataset')
        df = pd.read_csv(os.path.join(data_path, 'text_data.tsv'), sep='\t')
        if (is_category):
            df['Col2'] = df['Col2'].astype('category')
        data_table = DataTable(df)
        cs = DataTableColumnSelectionBuilder().include_col_names('Col1').build()
        learner = self._init_model()
        with pytest.raises(error_setting.ColumnUniqueValuesExceededError, match='is greater than allowed.'):
            _ = TrainModelModule.run(learner=learner, training_data=data_table, label_column_index_or_name=cs)

    def test_as_base_model_of_one_vs_all_classifier(self):
        binary_model = self._init_model()
        with pytest.raises(error_setting.InvalidLearnerError, match=f'has invalid type "{self.model_class.__name__}"'):
            _ = OneVsAllMulticlassModule.run(learner=binary_model)


class BinaryClassCommonCase(CommonBase):
    label_column_name = 'label'
    train_sample = mltest_utils.binary_class_sample
    performance_assert_function = mltest_utils.assert_greater

    def test_train_more_than_two_label(self):
        model = self._init_model()
        column_selection = DataTableColumnSelectionBuilder().include_col_names(
            MultiClassCommonCase.label_column_name).build()
        more_than_two_class_training_data = DataTable(MultiClassCommonCase.train_sample.train_df)
        with pytest.raises(expected_exception=error_setting.InvalidTrainingDatasetError,
                           match='The number of label classes should equal to 2'):
            _ = TrainModelModule.run(learner=model,
                                     training_data=more_than_two_class_training_data,
                                     label_column_index_or_name=column_selection)[0]

    def test_train_success(self):
        clf = self._init_model()
        df = self.train_sample.train_df
        result = TrainModelModule.run(learner=clf,
                                      training_data=DataTable(df),
                                      label_column_index_or_name=self.column_selection)
        assert isinstance(result, tuple)
        assert len(result) == 1
        assert isinstance(result[0], self.model_class)
        assert result[0].is_trained
        model = result[0]
        result = mltest_utils.get_f1(model)
        self.performance_assert_function(result, self.performance_assert_threshold)

    def test_evaluate_success(self):
        model = self._get_trained_model()
        model.label_column_name = 'label'
        scored_data = ScoreModelModule.run(
            learner=model,
            test_data=DataTable(self.train_sample.train_df),
            append_or_result_only=True)[0]
        result = EvaluateModelModule.run(
            scored_data=scored_data,
            scored_data_to_compare=None)
        assert isinstance(result, tuple)
        assert len(result) == 1
        evaluate_data = result[0]
        evaluate_data = evaluate_data.data if isinstance(evaluate_data, SideCarFileBundle) else evaluate_data
        assert isinstance(evaluate_data, DataTable)
        assert 'AUC' in evaluate_data.column_names
        assert 'Accuracy' in evaluate_data.column_names
        assert 'Precision' in evaluate_data.column_names
        assert 'Recall' in evaluate_data.column_names
        assert 'F1' in evaluate_data.column_names
        assert 'True Negative' in evaluate_data.column_names
        assert 'False Positive' in evaluate_data.column_names
        assert 'False Negative' in evaluate_data.column_names
        assert 'True Positive' in evaluate_data.column_names

    def test_cross_validate_success(self):
        clf = self._init_model()
        df = self.train_sample.train_df
        score_results, eval_results = CrossValidateModelModule.run(
            learner=clf,
            training_data=DataTable(df),
            label_column_index_or_name=self.column_selection,
            random_seed=0
        )
        assert isinstance(score_results, DataTable)
        assert 'Scored Labels' in score_results.column_names
        assert 'Fold Number' in score_results.column_names
        assert score_results.number_of_rows == self.train_sample.train_df.shape[0]
        assert isinstance(eval_results, DataTable)
        assert 'Fold Number' in eval_results.column_names
        assert 'Number of examples in fold' in eval_results.column_names
        assert 'AUC' in eval_results.column_names
        assert 'Accuracy' in eval_results.column_names
        assert 'Precision' in eval_results.column_names
        assert 'Recall' in eval_results.column_names
        assert 'F1' in eval_results.column_names
        assert 'True Negative' in eval_results.column_names
        assert 'False Positive' in eval_results.column_names
        assert 'False Negative' in eval_results.column_names
        assert 'True Positive' in eval_results.column_names

    def test_tse(self):
        clf = self._init_model()
        df = self.train_sample.train_df
        model = TrainModelModule.run(learner=clf,
                                     training_data=DataTable(df),
                                     label_column_index_or_name=self.column_selection)[0]
        scored_data = ScoreModelModule.run(
            learner=model,
            test_data=DataTable(self.train_sample.train_df),
            append_or_result_only=True)[0]
        result = EvaluateModelModule.run(
            scored_data=scored_data,
            scored_data_to_compare=None)[0]
        result = result.data if isinstance(result, SideCarFileBundle) else result
        self.performance_assert_function(result.data_frame['F1'].tolist()[0],
                                         self.performance_assert_threshold)

    def test_int_category_label_with_None(self):
        train_df = pd.DataFrame({'a': [1, 2, 1], 'b': [1, 2, None], 'label': [1, 2, None]}, dtype='category')
        test_df = pd.DataFrame({'a': [1, 2, None], 'b': [1, 2, 2], 'label': [1, None, 2]}, dtype='category')
        clf = self._init_model()
        column_selection = DataTableColumnSelectionBuilder().include_col_names('label').build()
        trained_learner = TrainModelModule.run(learner=clf,
                                               training_data=DataTable(train_df),
                                               label_column_index_or_name=column_selection)[0]
        scored_date = \
            ScoreModelModule.run(learner=trained_learner, test_data=DataTable(test_df), append_or_result_only=True)[0]
        assert scored_date.number_of_rows == 3
        EvaluateModelModule.run(scored_data=scored_date, scored_data_to_compare=None)

    def test_int_category_label_with_nan(self):
        train_df = pd.DataFrame({'a': [1, 2, 1], 'b': [1, 2, np.nan], 'label': [1, 2, np.nan]}, dtype='category')
        test_df = pd.DataFrame({'a': [1, 2, np.nan], 'b': [1, 2, 2], 'label': [1, np.nan, 2]}, dtype='category')
        clf = self._init_model()
        column_selection = DataTableColumnSelectionBuilder().include_col_names('label').build()
        trained_learner = TrainModelModule.run(learner=clf,
                                               training_data=DataTable(train_df),
                                               label_column_index_or_name=column_selection)[0]
        scored_date = \
            ScoreModelModule.run(learner=trained_learner, test_data=DataTable(test_df), append_or_result_only=True)[0]
        assert scored_date.number_of_rows == 3
        EvaluateModelModule.run(scored_data=scored_date, scored_data_to_compare=None)

    def test_str_category_label_with_None(self):
        train_df = pd.DataFrame(
            {'a': ['a', 'b', 'a', 'a'], 'b': ['a', 'b', 'a', 'b'], 'label': ['a', 'b', np.nan, 'b']}, dtype='category')
        test_df = pd.DataFrame(
            {'a': ['a', 'b', np.nan, 'b'], 'b': ['a', np.nan, 'b', 'a'], 'label': ['a', np.nan, 'b', 'b']},
            dtype='category')
        clf = self._init_model()
        column_selection = DataTableColumnSelectionBuilder().include_col_names('label').build()
        trained_learner = TrainModelModule.run(learner=clf,
                                               training_data=DataTable(train_df),
                                               label_column_index_or_name=column_selection)[0]
        scored_date = \
            ScoreModelModule.run(learner=trained_learner, test_data=DataTable(test_df), append_or_result_only=True)[0]
        assert scored_date.number_of_rows == 4
        EvaluateModelModule.run(scored_data=scored_date, scored_data_to_compare=None)

    def test_str_category_label_with_nan(self):
        train_df = pd.DataFrame(
            {'a': ['a', 'b', 'a', 'a'], 'b': ['a', 'b', 'a', 'b'], 'label': ['a', 'b', None, 'b']}, dtype='category')
        test_df = pd.DataFrame(
            {'a': ['a', 'b', None, 'b'], 'b': ['a', None, 'b', 'a'], 'label': ['a', None, 'b', 'b']},
            dtype='category')
        clf = self._init_model()
        column_selection = DataTableColumnSelectionBuilder().include_col_names('label').build()
        trained_learner = TrainModelModule.run(learner=clf,
                                               training_data=DataTable(train_df),
                                               label_column_index_or_name=column_selection)[0]
        scored_date = \
            ScoreModelModule.run(learner=trained_learner, test_data=DataTable(test_df), append_or_result_only=True)[0]
        assert scored_date.number_of_rows == 4
        EvaluateModelModule.run(scored_data=scored_date, scored_data_to_compare=None)

    @pytest.fixture()
    def input_data_table_multi_types(self):
        df = pd.DataFrame()
        df['int'] = [1, 10, np.nan, 12]
        df['float'] = [1.6, np.nan, 1, 0]
        df['string'] = [np.nan, '3', '1', '3']
        df['bool'] = [True, np.nan, False, np.nan]
        df['category'] = pd.Series([2, 1, 3, 1]).astype('category')
        df['datetime'] = pd.to_datetime(
            arg=pd.Series(['20190101', '20190103', np.nan, np.nan]), format='%Y%m%d', errors='coerce')
        df['timespan'] = pd.to_timedelta(
            arg=pd.Series([5, 10, np.nan, np.nan]), unit='days', errors='coerce')
        df['nan'] = [np.nan, np.nan, np.nan, np.nan]
        df['label'] = [1, 2, 1, 2]
        return DataTable(df)

    def test_mix_type_training_data(self, input_data_table_multi_types):
        clf = self._init_model()
        column_selection = DataTableColumnSelectionBuilder().include_col_names('label').build()
        trained_learner = TrainModelModule.run(learner=clf,
                                               training_data=input_data_table_multi_types,
                                               label_column_index_or_name=column_selection)[0]
        scored_date = \
            ScoreModelModule.run(learner=trained_learner, test_data=input_data_table_multi_types,
                                 append_or_result_only=True)[0]
        assert scored_date.number_of_rows == 4
        EvaluateModelModule.run(scored_data=scored_date, scored_data_to_compare=None)

    @pytest.fixture()
    def input_data_table_multi_category_types(self):
        df = pd.DataFrame()
        df['int'] = pd.Series([1, 10, np.nan, 12], dtype='category')
        df['float'] = pd.Series([1.6, np.nan, 1, 0], dtype='category')
        df['string'] = pd.Series([np.nan, '3', '1', '3'], dtype='category')
        df['bool'] = pd.Series([True, np.nan, False, np.nan], dtype='category')
        df['category'] = pd.Series([2, 1, 3, 1]).astype('category')
        df['datetime'] = pd.to_datetime(
            arg=pd.Series(['20190101', '20190103', np.nan, np.nan]), format='%Y%m%d', errors='coerce')
        df['timespan'] = pd.to_timedelta(
            arg=pd.Series([5, 10, np.nan, np.nan]), unit='days', errors='coerce')
        df['nan'] = [np.nan, np.nan, np.nan, np.nan]
        df['label'] = [1, 2, 1, 2]
        return DataTable(df)

    def test_mix_category_type_training_data(self, input_data_table_multi_category_types):
        clf = self._init_model()
        column_selection = DataTableColumnSelectionBuilder().include_col_names('label').build()
        trained_learner = TrainModelModule.run(learner=clf,
                                               training_data=input_data_table_multi_category_types,
                                               label_column_index_or_name=column_selection)[0]
        scored_date = \
            ScoreModelModule.run(learner=trained_learner, test_data=input_data_table_multi_category_types,
                                 append_or_result_only=True)[0]
        assert scored_date.number_of_rows == 4
        EvaluateModelModule.run(scored_data=scored_date, scored_data_to_compare=None)

    def test_training_on_one_class_data(self):
        clf = self._init_model()
        column_selection = DataTableColumnSelectionBuilder().include_col_names('label').build()
        one_class_training_data = DataTable(pd.DataFrame({'f1': [1, 2, 3], 'label': [1, 1, 1]}))
        with pytest.raises(expected_exception=error_setting.InvalidTrainingDatasetError,
                           match='The number of label classes should equal to 2'):
            _ = TrainModelModule.run(learner=clf,
                                     training_data=one_class_training_data,
                                     label_column_index_or_name=column_selection)[0]

    @pytest.mark.parametrize(
        'is_category',
        [True,
         False
         ]
    )
    def test_unique_values_data(self, is_category):
        data_path = os.path.join(mltest_utils.input_dataset_base_library(), 'unique_values_dataset')
        df = pd.read_csv(os.path.join(data_path, 'clientid_data.tsv'), sep='\t')
        if (is_category):
            df['Id'] = df['Id'].astype('category')
        data_table = DataTable(df)
        cs = DataTableColumnSelectionBuilder().include_col_names('Label').build()
        learner = self._init_model()
        with pytest.raises(error_setting.ColumnUniqueValuesExceededError, match='is greater than allowed.'):
            _ = TrainModelModule.run(learner=learner, training_data=data_table, label_column_index_or_name=cs)

    def test_as_base_model_of_one_vs_all_classifier(self):
        binary_model = self._init_model()
        one_vs_all_model, = OneVsAllMulticlassModule.run(learner=binary_model)
        training_data = DataTable(mltest_utils.multi_class_sample.train_df)
        test_data = DataTable(mltest_utils.multi_class_sample.train_df)
        cs = DataTableColumnSelectionBuilder().include_col_names('flower_type').build()

        trained_model, = TrainModelModule.run(learner=one_vs_all_model, training_data=training_data,
                                              label_column_index_or_name=cs)
        assert isinstance(trained_model.sub_model, self.model_class)
        _validate_estimators(binary_model.model, trained_model.model)
        scored_data, = ScoreModelModule.run(learner=trained_model, test_data=test_data, append_or_result_only=False)
        evaluate_result = evaluate_generic(scored_data=scored_data, scored_data_to_compare=None)
        metric_value = _get_metric_value(evaluate_result, metric_name=_TaskMetricName[TaskType.MultiClassification])
        assert metric_value > 0.9

    @pytest.mark.parametrize(
        'sweeping_mode', [SweepMethods.RandomSweep,
                          # todo :reduce search space. Too large search space, sweep EntireGrid would be extremely slow.
                          # SweepMethods.EntireGrid
                          ]
    )
    @pytest.mark.parametrize('cross_validation', [
        True, False
    ])
    def test_tune_one_vs_all_classifier(self, sweeping_mode, cross_validation):
        binary_model = self._init_range_model()
        one_vs_all_model, = OneVsAllMulticlassModule.run(learner=binary_model)
        if cross_validation:
            train_data = DataTable(mltest_utils.multi_class_sample.train_df)
            validation_data = None
        else:
            train_df, valid_df = mltest_utils.multi_class_sample.split_data
            train_data = DataTable(train_df)
            validation_data = DataTable(valid_df)
        test_data = DataTable(mltest_utils.multi_class_sample.train_df)
        cs = DataTableColumnSelectionBuilder().include_col_names('flower_type').build()
        report, model = TuneModelHyperParametersModule.run(
            predictor=one_vs_all_model,
            train_data=train_data,
            validation_data=validation_data,
            label_column_index_or_name=cs,
            sweeping_mode=sweeping_mode,
            binary_classification_metric=BinaryClassificationMetricType.Accuracy,
            regression_metric=RegressionMetricType.CoefficientOfDetermination,
            max_num_of_runs=5, random_seed=42, max_num_of_runs1=5,
            random_seed1=42)
        _check_report_columns(report, self.entry_class, self.default_range_parameter)
        scored_data, = ScoreModelModule.run(learner=model, test_data=test_data, append_or_result_only=False)
        # _validate_estimators(binary_model.model, trained_model.model) with parameter range
        evaluate_result = evaluate_generic(scored_data=scored_data, scored_data_to_compare=None)
        metric_value = _get_metric_value(evaluate_result, metric_name=_TaskMetricName[TaskType.MultiClassification])
        assert metric_value > 0.85


def _validate_estimators(sub_estimator, trained_model):
    estimator = trained_model.get_params().get('estimator', None)
    assert (estimator is not None)
    sub_params = sub_estimator.get_params()
    model_params = trained_model.get_params()
    for param, value in sub_params.items():
        # estimator__ is the prefix assigned to one-vs-rest classifier parameters by sklearn.
        assert model_params.get('estimator__' + param, None) == value


def _get_metric_value(evaluate_result, metric_name):
    return evaluate_result.data_frame.iloc[0].to_dict().get(metric_name, 0)


def _check_report_columns(report_data: DataTable, module, range_parameter):
    from azureml.studio.modulehost.module_reflector import ModuleEntry
    entry = ModuleEntry.from_func(module.run)
    parameter_annotations = entry.parameter_annotations
    for param_name, range_setting in range_parameter.items():
        if parameter_annotations[param_name].release_state == ReleaseState.Alpha:
            continue
        if not isinstance(range_setting, ParameterRangeSettings):
            continue
        friendly_name = parameter_annotations[param_name].friendly_name
        range_values = Sweepable.from_prs('test', range_setting).attribute_value
        assert friendly_name in report_data.column_names
        for i in report_data.get_column(friendly_name):
            assert i in range_values
