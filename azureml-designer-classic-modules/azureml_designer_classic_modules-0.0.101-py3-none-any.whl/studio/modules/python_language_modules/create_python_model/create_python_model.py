import os
import tempfile

import pandas as pd

from azureml.studio.modulehost.attributes import ScriptParameter, UntrainedLearnerOutputPort, ModuleMeta, ReleaseState
from azureml.studio.common.error import ErrorMapping, FailedToEvaluateScriptError, ColumnNotFoundError
from azureml.studio.core.logger import module_logger, TimeProfile
from azureml.studio.common.utils.inspectutils import assert_obj_has_attribute, assert_obj_has_method
from azureml.studio.core.utils.strutils import generate_random_string
from azureml.studio.modulehost.custom_module_utils import CustomModuleUtils
from azureml.studio.modulehost.module_reflector import BaseModule, module_entry
from azureml.studio.modules.ml.common.base_learner import BaseLearner
from azureml.studio.modules.ml.common.base_learner_setting import BaseLearnerSetting

PYTHON_MODEL_SAMPLE = """
# The script MUST define a class named AzureMLModel.
# This class MUST at least define the following three methods: "__init__", "train" and "predict".
# The signatures (method and argument names) of all these methods MUST be exactly the same as the following example.


import pandas as pd
from sklearn.linear_model import LogisticRegression


class AzureMLModel:
    # The __init__ method is only invoked in module "Create Python Model",
    # and will not be invoked again in the following modules "Train Model" and "Score Model".
    # The attributes defined in the __init__ method are preserved and usable in the train and predict method.
    def __init__(self):
        # self.model must be assigned
        self.model = LogisticRegression()
        self.feature_column_names = list()

    # Train model
    #   Param<df_train>: a pandas.DataFrame
    #   Param<df_label>: a pandas.Series
    def train(self, df_train, df_label):
        # self.feature_column_names record the names of columns used for training
        # It is recommended to set this attribute before training so that later the predict method
        # can use the columns with the same names as the train method
        self.feature_column_names = df_train.columns.tolist()
        self.model.fit(df_train, df_label)

    # Predict results
    #   Param<df>: a pandas.DataFrame
    #   Must return a pandas.DataFrame
    def predict(self, df):
        # Predict using the same column names as the training
        return pd.DataFrame({'Scored Labels': self.model.predict(df[self.feature_column_names])})
"""
SCRIPT_LANGUAGE = 'Python'
CUSTOM_MODEL_CLASS_NAME = 'AzureMLModel'
TRAIN_METHOD_NAME = 'train'
TRAIN_METHOD_ARGUMENTS = ['self', 'df_train', 'df_label']
PREDICT_METHOD_NAME = 'predict'
PREDICT_METHOD_ARGUMENTS = ['self', 'df']


class CustomModelProxy(BaseLearner):

    def __new__(cls, custom_model_cls_script: str, module_name=None):
        obj = super().__new__(cls)

        module = cls._load_script_to_module(custom_model_cls_script, module_name)
        obj.custom_model_cls = cls._load_custom_model_cls(module)

        # Record the custom_model_cls_script and module_name for __getnewargs__
        obj.custom_model_cls_script = custom_model_cls_script
        obj.module_name = module.__name__

        if module_name is None:
            module_logger.info(f"First time create {cls} instance.")
        else:
            module_logger.info(f"Create {cls} instance during reading pickle file.")

        return obj

    def __init__(self, *args, **kwargs):
        # CustomModelProxy initialization must only have one argument,
        # eg.: CustomModelProxy(custom_model_cls_script),
        # CustomModelProxy(custom_model_cls_script, module_name) is forbidden
        if len(args) + len(kwargs) != 1:
            raise ValueError(
                "__init__ function of class CustomModelProxy must have one argument")

        self.custom_model = self._initialize_and_validate_custom_model()
        super().__init__(setting=BaseLearnerSetting())

    def init_model(self):
        # To implement the abstract method init_model of BaseLearner
        pass

    def __getnewargs__(self):
        # pylint: disable=no-member
        return self.custom_model_cls_script, self.module_name

    def _initialize_and_validate_custom_model(self):
        # pylint: disable=no-member
        try:
            custom_model = self.custom_model_cls()
            self._validate_custom_model(custom_model)
        except Exception as ex:
            ErrorMapping.rethrow(ex, FailedToEvaluateScriptError(
                script_language=SCRIPT_LANGUAGE,
                message=f"Got exception when initializing custom model: '{ErrorMapping.get_exception_message(ex)}'."
            ))
        return custom_model

    def train(self, df: pd.DataFrame, label_column_name: str):
        """
        :param df: input training data
        :param label_column_name: label column name
        :return: None
        """

        # Record label/feature columns
        self.label_column_name = label_column_name
        self.init_feature_columns_names = df.columns.tolist()
        self.init_feature_columns_names.remove(label_column_name)

        # Check label column name and split df_train with df_label
        if label_column_name:
            if label_column_name not in df.columns:
                raise ColumnNotFoundError(column_id=label_column_name)

            df_label = df[label_column_name]
            df_train = df.drop(label_column_name, axis=1)

        # Invoke user-defined train method
        try:
            with TimeProfile('Train model'):
                self.custom_model.train(df_train, df_label)
        except Exception as ex:
            ErrorMapping.rethrow(ex, FailedToEvaluateScriptError(
                script_language=SCRIPT_LANGUAGE,
                message=f"Error occurred when invoking user-defined {TRAIN_METHOD_NAME} method: '{ex}'."
            ))

        # Tag the trained model
        self._is_trained = True

    def predict(self, test_data_df: pd.DataFrame):
        """
        :param test_data_df: input testing data
        :return: predicted data
        """

        try:
            with TimeProfile('Predict model'):
                predict_results = self.custom_model.predict(test_data_df)
                if not isinstance(predict_results, pd.DataFrame):
                    raise ValueError("prediction results must be a pandas DataFrame")

                # Verify if columns names of predict_results are all string
                ErrorMapping.verify_column_names_are_string(predict_results.columns)

        except Exception as ex:
            ErrorMapping.rethrow(ex, FailedToEvaluateScriptError(
                script_language=SCRIPT_LANGUAGE,
                message=f"Error occurred when invoking user-defined {PREDICT_METHOD_NAME} method: '{ex}'."
            ))

        return predict_results

    @staticmethod
    def _load_script_to_module(custom_model_cls_script: str, module_name: str = None):
        with tempfile.TemporaryDirectory() as temp_dir_name:
            if module_name is None:
                module_name = generate_random_string()

            # Prepare python script
            module_logger.info("Prepare python script")
            script_file = f"{module_name}.py"

            # Add current temporary directory into sys.path
            module_logger.info("Add current temporary directory into sys.path")
            CustomModuleUtils.add_directory_to_sys_path(temp_dir_name)

            with open(os.path.join(temp_dir_name, script_file), "w") as text_file:
                text_file.write(custom_model_cls_script)

            module_logger.info(f"Import custom module {module_name}")
            try:
                custom_module = __import__(module_name)
            except Exception as ex:
                ErrorMapping.rethrow(ex, FailedToEvaluateScriptError(
                    script_language=SCRIPT_LANGUAGE,
                    message=f"Got exception when importing script: '{ErrorMapping.get_exception_message(ex)}'."
                ))

        return custom_module

    @staticmethod
    def _load_custom_model_cls(custom_module):

        try:
            if hasattr(custom_module, CUSTOM_MODEL_CLASS_NAME):
                module_logger.info('Get custom model class')
                custom_model_cls = getattr(custom_module, CUSTOM_MODEL_CLASS_NAME)
            else:
                raise ValueError(f"{CUSTOM_MODEL_CLASS_NAME} is not found")

        except Exception as ex:
            ErrorMapping.rethrow(ex, FailedToEvaluateScriptError(
                script_language=SCRIPT_LANGUAGE,
                message=str(ex)
            ))

        return custom_model_cls

    @staticmethod
    def _validate_custom_model(custom_model):
        # custom module must define "model" attribute
        assert_obj_has_attribute(obj=custom_model, attr_name='model')

        # custom module must define "train" and "predict" methods
        assert_obj_has_method(obj=custom_model,
                              method_name=TRAIN_METHOD_NAME,
                              method_args=TRAIN_METHOD_ARGUMENTS)
        assert_obj_has_method(obj=custom_model,
                              method_name=PREDICT_METHOD_NAME,
                              method_args=PREDICT_METHOD_ARGUMENTS)


class CreatePythonModelModule(BaseModule):

    @staticmethod
    @module_entry(ModuleMeta(
        name="Create Python Model",
        description="Creates Python model using custom script",
        category="Python Language Modules",
        version="1.0",
        owner="Microsoft Corporation",
        family_id="a5b1e9d2-5c54-11e9-8647-d663bd873d93",
        release_state=ReleaseState.Release,
        is_deterministic=True,
    ))
    def run(
            python_stream_reader: ScriptParameter(
                name="Python Script",
                friendly_name="Python script",
                description="The Python script to execute",
                script_name="script.py",
                default_value=PYTHON_MODEL_SAMPLE
            )
    ) -> (
            UntrainedLearnerOutputPort(
                name="Untrained model",
                friendly_name="Untrained model",
                description="A untrained custom python model",
            ),
    ):
        input_values = locals()
        return CreatePythonModelModule._run_impl(**input_values)

    @classmethod
    def _run_impl(
        cls,
        python_stream_reader: str,
    ):
        custom_model_proxy = CustomModelProxy(python_stream_reader)

        return custom_model_proxy,
