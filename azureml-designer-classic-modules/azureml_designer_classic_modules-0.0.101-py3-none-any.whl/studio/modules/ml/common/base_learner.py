from abc import abstractmethod

import pandas as pd
from azureml.studio.core.logger import module_logger, time_profile, TimeProfile
from scipy.special import softmax

import azureml.studio.modules.ml.common.mathematic_op as mathematic_op
import azureml.studio.modules.ml.common.normalizer as normalizer
from azureml.studio.common.error import ErrorMapping, InvalidLearnerError, \
    MissingFeaturesError
from azureml.studio.modulehost.attributes import AutoEnum, ItemInfo
from azureml.studio.modules.ml.common.constants import ScoreColumnConstants
from .base_learner_setting import BaseLearnerSetting
from .ml_utils import TaskType, drop_illegal_label_instances, check_test_data_col_type_compatible


class CreateLearnerMode(AutoEnum):
    SingleParameter: ItemInfo(name="SingleParameter", friendly_name="Single Parameter") = ()
    ParameterRange: ItemInfo(name="ParameterRange", friendly_name="Parameter Range") = ()


class RestoreInfo:
    def __init__(self, param_name, inverse_func=None):
        """Restore the meaning of parameter from sklearn

        :param param_name: studio.parameter.friendly_name
        :param inverse_func: transform a scikit learn parameter value into the studio one.
                             If None, do not change the value
        """
        self.param_name = param_name
        self.inverse_func = inverse_func


class BaseLearner:
    def __init__(self, setting: BaseLearnerSetting, task_type=None):
        self.model = None
        self._is_trained = False
        self.init_feature_columns_names = None
        self.label_column_name = None
        self.normalized_feature_columns_names = None
        self.normalizer = None
        self.task_type = task_type
        self.setting = setting

    @property
    def parameter_mapping(self):
        return dict()

    @property
    def is_trained(self):
        return self._is_trained

    @property
    def parameter_range(self):
        return self.setting.parameter_range

    @abstractmethod
    def init_model(self):
        pass

    def _enable_verbose(self):
        verbose = getattr(self.model, 'verbose', None)
        if verbose is not None and verbose is not False and verbose == 0:
            """
            if verbose is None, verbose is not supported by this model
            if default verbose is False(not 0), enable it will cause two verbose output.
            only enable the model which was not enabled verbose.
            so only enable verbose when default verbose value is not (None, False).
            """
            self.model.set_params(verbose=1)

    @time_profile
    def train(self, df: pd.DataFrame, label_column_name: str):
        """Apply normalizing and training

        :param df: pandas.DataFrame, training data
        :param label_column_name: label column
        :return: None
        """

        # drop no label instances when training a supervised model.
        if label_column_name is not None:
            with TimeProfile("Removing instances with illegal label"):
                drop_illegal_label_instances(df, column_name=label_column_name, task_type=self.task_type)

        module_logger.info(
            f"validated training data has {df.shape[0]} Row(s) and {df.shape[1]} Columns.")
        # initial model
        with TimeProfile("Initializing model"):
            self.init_model()
            if self.setting.enable_log:
                module_logger.info("Enable Training Log.")
                self._enable_verbose()

        # record label column name and names of feature columns
        self.label_column_name = label_column_name
        self.init_feature_columns_names = df.columns.tolist()
        self.init_feature_columns_names.remove(label_column_name)
        with TimeProfile("Normalizing Data"):
            self._fit_normalize(df)
            train_x, train_y = self._apply_normalize(df, df.columns.tolist())

        self._train(train_x, train_y)

    @time_profile
    def _apply_normalize(self, df, df_transform_column_list=None):
        with TimeProfile("Applying feature normalization"):
            return self.normalizer.transform(df, df_transform_column_list)

    @time_profile
    def _fit_normalize(self, df):
        # normalize the data
        with TimeProfile("Initialing feature normalizer"):
            self.normalizer = normalizer.Normalizer()
            normalize_number = getattr(self.setting, 'normalize_features', True)
            self.normalizer.build(
                df=df,
                feature_columns=self.init_feature_columns_names,
                label_column_name=self.label_column_name,
                normalize_number=normalize_number,
                encode_label=self.task_type is not TaskType.Regression
            )
        with TimeProfile("Fitting feature normalizer"):
            self.normalizer.fit(df)

    @time_profile
    def _train(self, train_x, train_y):
        # train model
        with TimeProfile("Training Model"):
            self.model.fit(train_x, train_y)
        if hasattr(self.model, 'loss_'):
            module_logger.info(f'Training Loss: {self.model.loss_}.')
        if hasattr(self.model, 'n_iter_ '):
            module_logger.info(f'Inter Number: {self.model.n_iter_}.')
        self._is_trained = True

    @time_profile
    def _predict(self, test_x: pd.DataFrame):
        if hasattr(self.model, 'predict_proba'):
            with TimeProfile("Predicting probability"):
                prob = self.model.predict_proba(test_x)
            with TimeProfile("calculating argmax(Probability)"):
                label = prob.argmax(axis=1)
            return label, prob
        if hasattr(self.model, 'decision_function'):
            module_logger.info("Start calculating score.")
            with TimeProfile("Calculating Score"):
                prob = self.model.decision_function(test_x)
            with TimeProfile("Calculating Probability"):
                if len(prob.shape) == 2:
                    # The output is a matrix, matrix[i,j] indicates the score that
                    # the instances[i] is belong to the category[j].
                    # So, we normalize the score to get probabilities using the softmax function.
                    module_logger.info("Calculating Probability with the softmax function")
                    prob = softmax(prob, axis=1)
                    label = prob.argmax(axis=1)
                else:
                    # The output is a single column, indicates the score of being a positive label.
                    # So, we normalize the score to get probabilities using the sigmoid funciton.
                    module_logger.info("Calculating Probability with the sigmoid function")
                    label = prob > 1e-9
                    prob = mathematic_op.sigmoid(prob)
            return label, prob
        else:
            with TimeProfile("Predicting regression value"):
                return self.model.predict(test_x), None

    def _build_result_dataframe(self, label, prob):
        """Build scored result dataframe, with predefined column names.

        Both MachineLearningConstants.PREDICT_LABEL_COLUMN_NAME and ScoreColumnConstants.ScoredLabelsColumnName are
        "Scored Label". Since ScoreColumnConstants substituted the MachineLearningConstants, replace the
        MachineLearningConstants with ScoreColumnConstants.
        """
        result_df = pd.DataFrame()
        if self.task_type == TaskType.BinaryClassification:
            module_logger.info('Binary Classification Task, Result Contains Scored Label and Scored Probability')
            # If prob contains the probabilities of each class, choose the positive class probability
            if len(prob.shape) == 2:
                # Tree model like boosted decision tree and decision forest support one class label data,
                # but the boosted decision tree will return [n, 2] with trained label in first column
                # while decision forest return [n, 1]
                # label_classes_len takes the number of classes
                # and choose the last one as the positive label column id.
                classes_attr = getattr(self.model, 'classes_', None)
                # classes_attr will be numpy.array or None,
                # So use classes_attr is not None to check it is not null,
                # use classes_attr.size != 0 to test it is not empty.
                # Simply use 'if classes_attr' will fail if classes_attr is array.
                if classes_attr is not None and classes_attr.size != 0:
                    classes_num = classes_attr.size
                    module_logger.info(f"Found {classes_num} label classes in classes_ attribute.")
                    label_column_index = classes_num - 1
                    module_logger.info(f"Using {label_column_index} as probability column.")
                else:
                    label_column_index = 1
                    module_logger.info(f"Take the second column as probability column by default.")

                prob = prob[:, label_column_index]
            result_df[ScoreColumnConstants.ScoredLabelsColumnName] = \
                self.normalizer.inverse_transform(label, label_column=self.label_column_name)
            result_df[ScoreColumnConstants.ScoredProbabilitiesColumnName] = prob
        elif self.task_type == TaskType.MultiClassification:
            module_logger.info('MultiClass Classification Task, Result Contains Scored Label and Scored Probability')
            result_df = pd.DataFrame(
                data=prob,
                columns=[f'{ScoreColumnConstants.ScoredProbabilitiesMulticlassColumnNamePattern}_{str(i)}'
                         for i in range(prob.shape[1])])
            result_df[ScoreColumnConstants.ScoredLabelsColumnName] = \
                self.normalizer.inverse_transform(label, label_column=self.label_column_name)
        elif self.task_type == TaskType.Regression:
            module_logger.info('Regression Task, Result Contains Scored Label')
            result_df[ScoreColumnConstants.ScoredLabelsColumnName] = label
        else:
            ErrorMapping.throw(InvalidLearnerError(self.model.__class__.__name__))
        return result_df

    def predict(self, test_data_df):
        self._validate_no_missing_feature(input_feature_list=test_data_df.columns.tolist())
        test_x = test_data_df[self.init_feature_columns_names]
        module_logger.info(f'Check if column types of test data are consistent with train data')
        check_test_data_col_type_compatible(test_x,
                                            self.normalizer.feature_columns_categorized_by_type,
                                            self.setting, self.task_type)
        module_logger.info(f'Successfully checked column types. Predicting.')
        test_x, _ = self._apply_normalize(test_x, test_x.columns.tolist())
        label, prob = self._predict(test_x)
        module_logger.info(f'Successfully predicted.')
        return self._build_result_dataframe(label, prob)

    def _validate_no_missing_feature(self, input_feature_list):
        missing_feature_list = [feature for feature in self.init_feature_columns_names if
                                feature not in input_feature_list]

        if missing_feature_list:
            ErrorMapping.throw(MissingFeaturesError(required_feature_name=';'.join(missing_feature_list)))
