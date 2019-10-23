import numpy as np
import pandas as pd
import scipy.sparse
from sklearn.metrics import make_scorer
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
from sklearn.model_selection import PredefinedSplit

import azureml.studio.modules.ml.common.metric_calculator as metric_calculator
import azureml.studio.modules.ml.common.ml_utils as ml_utils
from azureml.studio.core.logger import module_logger, TimeProfile, time_profile
from azureml.studio.modulehost.attributes import AutoEnum, ReleaseState
from azureml.studio.modulehost.attributes import ItemInfo
from azureml.studio.modules.ml.common.base_learner import BaseLearner
from azureml.studio.modules.ml.common.base_learner_setting import BaseLearnerSetting
from azureml.studio.modules.ml.initialize_models.binary_classifier import AveragePerceptronBiClassifier, \
    SupportVectorMachineBiClassifier


class SweepMethods(AutoEnum):
    EntireGrid: ItemInfo(name="Entire grid", friendly_name="Entire grid") = ()
    RandomSweep: ItemInfo(name="Random sweep", friendly_name="Random sweep") = ()
    RandomGrid: ItemInfo(name="Random grid", friendly_name="Random grid", release_state=ReleaseState.Alpha) = ()


class BinaryClassificationMetricType(AutoEnum):
    Accuracy: ItemInfo(name="Accuracy", friendly_name="Accuracy") = ()
    Precision: ItemInfo(name="Precision", friendly_name="Precision") = ()
    Recall: ItemInfo(name="Recall", friendly_name="Recall") = ()
    FScore: ItemInfo(name="F-score", friendly_name="F-score") = ()
    AUC: ItemInfo(name="AUC", friendly_name="AUC") = ()
    AverageLogLoss: ItemInfo(name="Average Log Loss", friendly_name="Average Log Loss") = ()
    TrainLogLos: ItemInfo(name="Train Log Loss", friendly_name="Train Log Loss", release_state=ReleaseState.Alpha) = ()


class RegressionMetricType(AutoEnum):
    MeanAbsoluteError: ItemInfo(name="Mean absolute error",
                                friendly_name="Mean absolute error") = ()
    RootMeanSquaredError: ItemInfo(name="Root of mean squared error",
                                   friendly_name="Root of mean squared error") = ()
    RelativeAbsoluteError: ItemInfo(name="Relative absolute error",
                                    friendly_name="Relative absolute error") = ()
    RelativeSquaredError: ItemInfo(name="Relative squared error",
                                   friendly_name="Relative squared error") = ()
    CoefficientOfDetermination: ItemInfo(name="Coefficient of determination",
                                         friendly_name="Coefficient of determination") = ()


class MapMetricToScorer:
    binary_metric_map = {
        BinaryClassificationMetricType.Accuracy: 'accuracy',
        BinaryClassificationMetricType.Precision: 'precision',
        BinaryClassificationMetricType.Recall: 'recall',
        BinaryClassificationMetricType.FScore: 'f1',
        BinaryClassificationMetricType.AUC: 'roc_auc',
        BinaryClassificationMetricType.AverageLogLoss: 'neg_log_loss',
    }
    regression_metric_map = {
        RegressionMetricType.MeanAbsoluteError: 'neg_mean_absolute_error',
        RegressionMetricType.RootMeanSquaredError: make_scorer(
            metric_calculator.root_mean_squared_error, greater_is_better=False),
        RegressionMetricType.RelativeAbsoluteError: make_scorer(
            metric_calculator.relative_absolute_error, greater_is_better=False),
        RegressionMetricType.RelativeSquaredError: make_scorer(
            metric_calculator.relative_squared_error, greater_is_better=False),
        RegressionMetricType.CoefficientOfDetermination: 'r2'
    }

    @classmethod
    def customize_metric(self, scorer, metric, customized_scorer):
        scorer[ItemInfo.get_enum_friendly_name(metric)] = customized_scorer
        return scorer

    @classmethod
    def get_scorer(cls, task_type, binary_metric, regression_metric, customize_log_loss):
        """Prepare scorer and metric friendly_name

        Get all metric scorers for a specific task. The scorer would be a dict<metric_friendly_name, metric_calculator>.
        Then, according to the provided metric, return the corresponding friendly name.
        """
        if task_type == ml_utils.TaskType.BinaryClassification:
            binary_scorer = {
                ItemInfo.get_enum_friendly_name(x): cls.binary_metric_map[x] for x in
                BinaryClassificationMetricType
                if x in cls.binary_metric_map
            }
            if customize_log_loss:
                binary_scorer = cls.customize_metric(
                    scorer=binary_scorer,
                    metric=BinaryClassificationMetricType.AverageLogLoss,
                    customized_scorer=make_scorer(metric_calculator.log_loss, greater_is_better=False,
                                                  needs_threshold=True))
            return binary_scorer, ItemInfo.get_enum_friendly_name(binary_metric)
        elif task_type == ml_utils.TaskType.Regression:
            regression_scorer = {
                ItemInfo.get_enum_friendly_name(x): cls.regression_metric_map[x] for x in
                RegressionMetricType
                if x in cls.regression_metric_map
            }
            return regression_scorer, ItemInfo.get_enum_friendly_name(regression_metric)
        elif task_type == ml_utils.TaskType.MultiClassification:
            multiclass_scorer = {
                ItemInfo.get_enum_friendly_name(BinaryClassificationMetricType.Accuracy): cls.binary_metric_map[
                    BinaryClassificationMetricType.Accuracy]}
            return multiclass_scorer, 'Accuracy'
        else:
            raise TypeError(f'Error task type {task_type}')


class LearnerParameterSweeperSetting(BaseLearnerSetting):
    def __init__(self, sweeping_mode: SweepMethods,
                 binary_classification_metric: BinaryClassificationMetricType,
                 regression_metric: RegressionMetricType, max_num_of_runs: int = None,
                 random_seed: int = None):
        super().__init__()
        self.sweeping_mode = sweeping_mode
        self.binary_classification_metric = binary_classification_metric
        self.regression_metric = regression_metric
        self.max_num_of_runs = max_num_of_runs
        self.random_number_seed = random_seed

    def init_range(self):
        pass

    def init_single(self):
        pass


class LearnerParameterSweeper(BaseLearner):
    _PARAMETER_PREFIX = 'param_'
    _TEST_DATA_METRIC_PREFIX = 'mean_test_'
    DEFAULT_NUMBER_OF_FOLDS = 3  # Default number of folds before scikit-learn v0.22, will change from 3 to 5 in v0.22.

    def __init__(self, setting, task_type, sub_model: BaseLearner):
        super().__init__(setting, task_type)
        self.sub_model = sub_model

    def gen_inter_name(self, name):
        return self._PARAMETER_PREFIX + name

    @property
    def parameter_range(self):
        return self.sub_model.parameter_range

    def _restore_param_column(self, df: pd.DataFrame):
        for column_name, restore_info in self.sub_model.parameter_mapping.items():
            inter_name = self.gen_inter_name(name=column_name)
            new_name = restore_info.param_name
            func = restore_info.inverse_func
            df.rename(columns={inter_name: new_name}, inplace=True)
            if func is not None:
                df[new_name] = df[new_name].apply(func)
        return df

    def get_report(self):
        """Build the report data from the searched result.

        This method process the cross-validation result generated by the *SearchCV model, by useful columns,
        renaming the column and transforming the parameter value.

        The `self.model.cv_results` stores the corresponding evaluation results of different hyper-parameters,
        it could be imported into a pandas DataFrame.
        The columns startswith _PARAMETER_PREFIX are used to store a list of parameter settings for all the parameter
        candidates. The columns startswith _TEST_DATA_METRIC_PREFIX are used to store the evaluation results.
        See this doc https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GridSearchCV.html to find
        some sample outputs.

        Since the name and meaning of input parameters in VI are different from the scikit learn,
        we need to rename the column names to our friendly names and do some transformations.
        """
        df = pd.DataFrame(self.model.cv_results_)
        keep_columns = [x for x in df.columns.tolist() if
                        x.startswith(self._PARAMETER_PREFIX) or x.startswith(self._TEST_DATA_METRIC_PREFIX)]
        report_df = df[keep_columns]
        report_df['rank'] = df['rank_test_' + self.model.refit]
        report_df = report_df.sort_values(by='rank')
        report_df.reset_index(drop=True, inplace=True)
        report_df = self._restore_param_column(report_df)
        return report_df

    def set_pre_split(self, train_num, valid_num):
        with TimeProfile("Build predefined split"):
            split_array = np.zeros(train_num + valid_num)
            # The last valid rows are validation dataset
            split_array[-valid_num:] = -1
            ps = PredefinedSplit(split_array)
        self.model.set_params(cv=ps)

    def concat_train_and_validation(self, train_x, train_y, valid_x, valid_y):
        """Build a full dataset with the train dataset and the validation dataset.

        When evaluating different hyperparameters for models, if the validation dataset is not empty, the training
        dataset would be used to train a model, while the validation dataset would be used to select hyper-parameters.
        scikit-learn does not support explicit use of a validation dataset, but does support the custom-defined
        validation splitting strategy. Since the PredefinedSplit provides train/test indices to split data,
        we can combine the two datasets and use PredefinedSplit to define the splitting strategy,
        so that we could specify the validation data.
        """
        train_y = np.concatenate((train_y, valid_y), axis=None)
        if isinstance(train_x, pd.DataFrame):
            train_x = pd.concat([train_x, valid_x], ignore_index=True)
        elif isinstance(train_x, np.ndarray):
            # When all features are numerical.
            train_x = np.vstack([train_x, valid_x])
        else:
            # When training data contains any str/category feature.
            train_x = scipy.sparse.vstack([train_x, valid_x])
        return train_x, train_y

    @time_profile
    def train(self, df: pd.DataFrame, label_column_name: str, valid_df=None):
        """Apply normalizing and training

        :param df: pandas.DataFrame, training data
        :param label_column_name: label column
        :param valid_df[opt], pandas.DataFrame(), validation data
        :return: None
        """

        # drop no label instances when training a supervised model.
        df = self._clean_training_data(df, label_column_name)
        # initial model
        with TimeProfile("Initializing model"):
            self.init_model()
            if self.setting.enable_log:
                module_logger.info("Enable Training Log.")
                self._enable_verbose()

        # record label column name and names of feature columns
        self.sub_model._record_column_names(df.columns.tolist(), label_column_name)
        train_x, train_y = self.sub_model._normalize_data(df)

        if valid_df is not None:
            valid_df = self._clean_training_data(valid_df, label_column_name)
            # concat training dataset and validation dataset, and build up pre_split.
            self.set_pre_split(df.shape[0], valid_df.shape[0])
            valid_x, valid_y = self.sub_model._apply_normalize(valid_df, valid_df.columns.tolist())
            train_x, train_y = self.concat_train_and_validation(train_x, train_y, valid_x, valid_y)
        else:
            # cross-validation should be used when selecting hyper-parameters, if validation data does not be explicitly
            # specified, K-fold cross validation would be used. The default K of scikit-learn will be changed in the
            # future, so we would better do not use the default value.
            self.model.set_params(cv=self.DEFAULT_NUMBER_OF_FOLDS)
        self._train(train_x, train_y)

    def get_best_model(self):
        best_model = self.model.best_estimator_
        sub_model = self.sub_model
        sub_model.model = best_model
        sub_model._is_trained = True
        return sub_model

    def init_model(self):
        self.sub_model.init_model()
        scorer, metric = MapMetricToScorer.get_scorer(
            task_type=self.task_type,
            binary_metric=self.setting.binary_classification_metric,
            regression_metric=self.setting.regression_metric,
            customize_log_loss=isinstance(self.sub_model,
                                          (AveragePerceptronBiClassifier, SupportVectorMachineBiClassifier))
        )
        if self.setting.sweeping_mode == SweepMethods.EntireGrid:
            self.model = GridSearchCV(self.sub_model.model, param_grid=[self.parameter_range],
                                      scoring=scorer, refit=metric)
        else:
            self.model = RandomizedSearchCV(self.sub_model.model, param_distributions=self.parameter_range,
                                            random_state=self.setting.random_number_seed, scoring=scorer,
                                            refit=metric, n_iter=self.setting.max_num_of_runs)
