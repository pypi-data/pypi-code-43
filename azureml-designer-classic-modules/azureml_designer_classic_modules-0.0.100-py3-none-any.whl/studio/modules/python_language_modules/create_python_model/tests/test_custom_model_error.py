import re

import pytest

from azureml.studio.common.datatable.data_table import DataTableColumnSelectionBuilder
from azureml.studio.common.error import FailedToEvaluateScriptError, ColumnNotFoundError, ColumnNamesNotStringError
from azureml.studio.modules.ml.score.score_generic_module.score_generic_module import ScoreModelModule
from azureml.studio.modules.ml.train.train_generic_model.train_generic_model import TrainModelModule
from azureml.studio.modules.python_language_modules.create_python_model.create_python_model import \
    CreatePythonModelModule
from azureml.studio.modules.python_language_modules.create_python_model.create_python_model import SCRIPT_LANGUAGE, \
    CUSTOM_MODEL_CLASS_NAME, TRAIN_METHOD_NAME, PREDICT_METHOD_NAME, TRAIN_METHOD_ARGUMENTS, PREDICT_METHOD_ARGUMENTS
from azureml.studio.modules.python_language_modules.create_python_model.tests.test_custom_model_binary_classification\
    import binary_classification_training_data, label_column, binary_classification_predict_data
from azureml.studio.modulehost.module_invoker import execute


def evaluate_script_error_template(error_message: str):
    return f'The following error occurred during script evaluation, please view the output log for more information:\n'\
        f'---------- Start of error message from {SCRIPT_LANGUAGE} interpreter ----------\n' \
        f'{error_message}\n' \
        f'---------- End of error message from {SCRIPT_LANGUAGE}  interpreter  ----------'


@pytest.mark.parametrize(
    'script,expect_error_message',
    [
        ("""
# Unknown module name
import PANDAS as pd
""", "Got exception when importing script: 'No module named 'PANDAS''."),
        ("""
import pandas as pd
from sklearn.linear_model import LinearRegression

# Unknown class name in global level
setting = ParameterRangeSettings()

class AzureMLModel:
    def __init__(self):
        self.model = LinearRegression()

    def train(self, df_train, df_label):
        self.model.fit(df_train, df_label)

    def predict(self, df):
        return pd.DataFrame({'Scored Labels': self.model.predict(df)})
""", "Got exception when importing script: 'name 'ParameterRangeSettings' is not defined'."),
        ("""
import pandas as pd
from sklearn.linear_model import LinearRegression

class AzureMLModel:
    def __init__(self):
        self.model = LinearRegression()
        # Unknown class name in __init__ method
        setting = ParameterRangeSettings()

    def train(self, df_train, df_label):
        self.model.fit(df_train, df_label)

    def predict(self, df):
        return pd.DataFrame({'Scored Labels': self.model.predict(df)})
""", "Got exception when initializing custom model: 'name 'ParameterRangeSettings' is not defined'.")
    ]
)
def test_error_load_script_to_module(script, expect_error_message):
    err_message = evaluate_script_error_template(expect_error_message)
    with pytest.raises(FailedToEvaluateScriptError, match=err_message):
        CreatePythonModelModule.run(python_stream_reader=script)


def test_error_load_custom_model_cls():
    script = """
class azuremlmodel:
    pass
"""
    err_message = evaluate_script_error_template(f'{CUSTOM_MODEL_CLASS_NAME} is not found')
    with pytest.raises(FailedToEvaluateScriptError, match=err_message):
        CreatePythonModelModule.run(python_stream_reader=script)


"""
Test errors occurred in _validate_custom_model
"""


def test_not_define_model_error():
    script = """
class AzureMLModel:
    def __init__(self):
        self.model = None
"""
    err_message = evaluate_script_error_template(
        f"Got exception when initializing custom model:"
        f" '{CUSTOM_MODEL_CLASS_NAME} object must define attribute 'model''.")
    with pytest.raises(FailedToEvaluateScriptError, match=err_message):
        CreatePythonModelModule.run(python_stream_reader=script)


def test_not_define_train_error():
    script = """
from sklearn.linear_model import LogisticRegression


class AzureMLModel:
    def __init__(self):
        self.model = LogisticRegression()
"""
    err_message = evaluate_script_error_template(
        f"Got exception when initializing custom model:"
        f" '{CUSTOM_MODEL_CLASS_NAME} object must define method '{TRAIN_METHOD_NAME}''.")
    with pytest.raises(FailedToEvaluateScriptError, match=err_message):
        CreatePythonModelModule.run(python_stream_reader=script)


def test_not_define_predict_error():
    script = """
from sklearn.linear_model import LogisticRegression


class AzureMLModel:
    def __init__(self):
        self.model = LogisticRegression()

    def train(self, df_train, df_label):
        self.model.fit(df_train, df_label)
"""
    err_message = evaluate_script_error_template(
        f"Got exception when initializing custom model:"
        f" '{CUSTOM_MODEL_CLASS_NAME} object must define method '{PREDICT_METHOD_NAME}''.")
    with pytest.raises(FailedToEvaluateScriptError, match=err_message):
        CreatePythonModelModule.run(python_stream_reader=script)


def test_input_arguments_train_error():
    script = """
from sklearn.linear_model import LogisticRegression


class AzureMLModel:
    def __init__(self):
        self.model = LogisticRegression()

    def train(self, DF_TRAIN, DF_LABEL):
         self.model.fit(DF_TRAIN, DF_LABEL)

    def predict(self, df):
        return pd.DataFrame({'Scored Labels': self.model.predict(df)})
"""
    err_message = evaluate_script_error_template(
        f"Got exception when initializing custom model:"
        f" '{TRAIN_METHOD_NAME} method must have argument list: {TRAIN_METHOD_ARGUMENTS}'.")
    with pytest.raises(FailedToEvaluateScriptError, match=re.escape(err_message)):
        CreatePythonModelModule.run(python_stream_reader=script)


def test_input_arguments_predict_error():
    script = """
from sklearn.linear_model import LogisticRegression


class AzureMLModel:
    def __init__(self):
        self.model = LogisticRegression()

    def train(self, df_train, df_label):
        self.model.fit(df_train, df_label)

    def predict(self, DF):
        return pd.DataFrame({'Scored Labels': self.model.predict(df)})
"""
    err_message = evaluate_script_error_template(
        f"Got exception when initializing custom model:"
        f" '{PREDICT_METHOD_NAME} method must have argument list: {PREDICT_METHOD_ARGUMENTS}'.")
    with pytest.raises(FailedToEvaluateScriptError, match=re.escape(err_message)):
        CreatePythonModelModule.run(python_stream_reader=script)


@pytest.mark.parametrize(
    'script,expect_error_message',
    [
        ("""
from sklearn.linear_model import LogisticRegression


class AzureMLModel:
    def __init__(self):
        self.model = LogisticRegression()

    def train(self, df_train, df_label):
        raise ValueError('value error')
        self.model.fit(df_train, df_label)

    def predict(self, df):
        return pd.DataFrame({'Scored Labels': self.model.predict(df)})
""", f"Error occurred when invoking user-defined {TRAIN_METHOD_NAME} method: 'value error'."),
        ("""
import pandas as pd
from sklearn.linear_model import LinearRegression

class AzureMLModel:
    def __init__(self):
        self.model = LinearRegression()

    def train(self, df_train, df_label):
        # Unknown class name in train method
        setting = ParameterRangeSettings()
        self.model.fit(df_train, df_label)

    def predict(self, df):
        return pd.DataFrame({'Scored Labels': self.model.predict(df)})
""", f"Error occurred when invoking user-defined {TRAIN_METHOD_NAME} method:"
         f" 'name 'ParameterRangeSettings' is not defined'.")
    ]
)
def test_error_train_custom_model(script, expect_error_message):
    err_message = evaluate_script_error_template(expect_error_message)
    with pytest.raises(FailedToEvaluateScriptError, match=err_message):
        init_model = CreatePythonModelModule.run(python_stream_reader=script)[0]
        TrainModelModule.run(
            learner=init_model,
            training_data=binary_classification_training_data(),
            label_column_index_or_name=label_column()
        )


@pytest.mark.parametrize(
    'script,expect_error_message',
    [
        ("""
from sklearn.linear_model import LogisticRegression


class AzureMLModel:
    def __init__(self):
        self.model = LogisticRegression()

    def train(self, df_train, df_label):
        self.model.fit(df_train, df_label)

    def predict(self, df):
        return {'Scored Labels': self.model.predict(df)}
""", f"Error occurred when invoking user-defined {PREDICT_METHOD_NAME} method:"
         f" 'prediction results must be a pandas DataFrame'."),
        ("""
import pandas as pd
from sklearn.linear_model import LinearRegression

class AzureMLModel:
    def __init__(self):
        self.model = LinearRegression()

    def train(self, df_train, df_label):
        self.model.fit(df_train, df_label)

    def predict(self, df):
        # Unknown class name in predict method
        setting = ParameterRangeSettings()
        return pd.DataFrame({'Scored Labels': self.model.predict(df)})
""", f"Error occurred when invoking user-defined {PREDICT_METHOD_NAME} method:"
         f" 'name 'ParameterRangeSettings' is not defined'.")
    ]
)
def test_error_predict_custom_model(script, expect_error_message):
    err_message = evaluate_script_error_template(expect_error_message)
    with pytest.raises(FailedToEvaluateScriptError, match=err_message):
        init_model = CreatePythonModelModule.run(python_stream_reader=script)[0]
        trained_model = TrainModelModule.run(
            learner=init_model,
            training_data=binary_classification_training_data(),
            label_column_index_or_name=label_column()
        )[0]
        ScoreModelModule.run(
            learner=trained_model,
            test_data=binary_classification_predict_data(),
            append_or_result_only=True
        )


def test_column_not_found_error_in_train():
    script = """
from sklearn.linear_model import LogisticRegression


class AzureMLModel:
    def __init__(self):
        self.model = LogisticRegression()

    def train(self, df_train, df_label):
        self.model.fit(df_train, df_label)

    def predict(self, df):
        return pd.DataFrame({'Scored Labels': self.model.predict(df)})
"""
    err_message = 'Column with name or index "col3" not found'
    wrong_label_column = DataTableColumnSelectionBuilder().include_col_names('col3').build()
    with pytest.raises(ColumnNotFoundError, match=err_message):
        init_model = CreatePythonModelModule.run(python_stream_reader=script)[0]
        TrainModelModule.run(
            learner=init_model,
            training_data=binary_classification_training_data(),
            label_column_index_or_name=wrong_label_column
        )


def test_column_names_not_string_error_in_predict():
    script = """
import pandas as pd
from sklearn.linear_model import LogisticRegression


class AzureMLModel:
    def __init__(self):
        self.model = LogisticRegression()

    def train(self, df_train, df_label):
        self.model.fit(df_train, df_label)

    def predict(self, df):
        return pd.DataFrame({1: self.model.predict(df)})
"""
    expect_error_message = 'Column names: [[]1[]] are not string'
    with pytest.raises(ColumnNamesNotStringError, match=rf".*{expect_error_message}.*"):
        init_model = CreatePythonModelModule.run(python_stream_reader=script)[0]
        trained_model = TrainModelModule.run(
            learner=init_model,
            training_data=binary_classification_training_data(),
            label_column_index_or_name=label_column()
        )[0]
        ScoreModelModule.run(
            learner=trained_model,
            test_data=binary_classification_predict_data(),
            append_or_result_only=True
        )


def test_pickle_dump_error(tmp_path):
    script = """
from threading import Lock
class AzureMLModel:
    def __init__(self):
        self.model = 'model'
        self.lock = Lock()

    def train(self, df_train, df_label):
        pass

    def predict(self, df):
        return pd.DataFrame()
"""
    original_msg = "can't pickle _thread.lock objects"
    expected_error_message = f"Got exception when dumping custom model with pickle: '{original_msg}'"
    with pytest.raises(FailedToEvaluateScriptError, match=expected_error_message):
        cmds = [
            '--module-name=azureml.studio.modules.python_language_modules.create_python_model',
            f'--untrained-model={tmp_path}',
            '--python-script',
            script,
            ]
        execute(cmds)
