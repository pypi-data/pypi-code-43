import pandas as pd
import numpy as np

import pytest

from azureml.studio.common.datatable.data_table import DataTable
from azureml.studio.common.error import FailedToEvaluateScriptError
from azureml.studio.common.zip_wrapper import ZipFileWrapper
from azureml.studio.modules.python_language_modules.execute_python_script import ExecutePythonScriptModule

DATA_TABLE_1 = DataTable(
        pd.DataFrame(
            columns=["A", "B"],
            data=[
                [0, 1],
                [2, 3],
                [4, 5],
                [6, 7]
            ]))

DATA_TABLE_2 = DataTable()


@pytest.fixture
def input_data_table_1():
    return DATA_TABLE_1


@pytest.fixture
def input_data_table_2():
    return DATA_TABLE_2


@pytest.mark.parametrize(
    "script", [
        ("""
import pandas as pd

def azureml_main(dataframe1 = None, dataframe2 = None):
    # Recommended output as a Tuple
    return dataframe1,dataframe2
"""),
        ("""
import pandas as pd

def azureml_main(dataframe1 = None, dataframe2 = None):
    # Recommended output as a Tuple
    return dataframe1,
"""),
        ("""
import pandas as pd

def azureml_main(dataframe1 = None, dataframe2 = None):
    # Accepted output - a dataframe only
    return dataframe1
""")])
def test_execute_python_script(input_data_table_1, input_data_table_2, script):
    # pylint: disable=no-value-for-parameter
    result = ExecutePythonScriptModule.run(
        dataset1=input_data_table_1,
        dataset2=input_data_table_2,
        python_stream_reader=script
    )[0]

    assert result.data_frame.equals(input_data_table_1.data_frame)


@pytest.mark.parametrize(
    "input_data_set_1, input_data_set_2", [
        (DATA_TABLE_1, None),
        (None, DATA_TABLE_2),
        (None, None)])
def test_execute_python_script_with_empty_input(input_data_set_1, input_data_set_2):
    script = """
import pandas as pd

def azureml_main(dataframe1 = None, dataframe2 = None):

    return pd.DataFrame(columns=["A"], data=[[0]]),
"""
    # pylint: disable=no-value-for-parameter
    result = ExecutePythonScriptModule.run(
        dataset1=input_data_set_1,
        dataset2=input_data_set_2,
        python_stream_reader=script
    )[0]

    assert result.data_frame.equals(pd.DataFrame(columns=["A"], data=[[0]]))


@pytest.mark.parametrize(
    "script", [
        ("""
import pandas as pd

def azureml_main(dataframe1 = None, dataframe2 = None):
    # Accepted output - nothing return
    return
"""),
        ("""
import pandas as pd

def azureml_main(dataframe1 = None, dataframe2 = None):
    # Accepted output - no return
    pass
""")])
def test_execute_python_script_empty_output(input_data_table_1, input_data_table_2, script):
    # pylint: disable=no-value-for-parameter
    result = ExecutePythonScriptModule.run(
        dataset1=input_data_table_1,
        dataset2=input_data_table_2,
        python_stream_reader=script
    )

    assert all(x.data_frame.equals(DataTable().data_frame) for x in result)


def test_execute_python_script_with_bundle_zip(tmpdir, input_data_table_1, input_data_table_2):
    import os

    custom_bundle_script = """
def my_func(dataframe1):
    return dataframe1
"""

    script_file = "my_script.py"
    script_file_path = tmpdir.join(script_file)
    with open(script_file_path, "w") as text_file:
        text_file.write(custom_bundle_script)

    text_file = "my_sample.txt"
    custom_sample = "Hello World!"
    text_file_path = tmpdir.join(text_file)
    with open(text_file_path, "w") as text_file:
        text_file.write(custom_sample)

    bundle_zip = "bundle.zip"
    bundle_zip_path = tmpdir.join(bundle_zip)
    import zipfile
    with zipfile.ZipFile(bundle_zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.write(script_file_path, arcname=os.path.basename(script_file_path))
        zip_file.write(text_file_path, arcname=os.path.basename(text_file_path))

    script = """
import pandas as pd
from my_script import my_func

def azureml_main(dataframe1 = None, dataframe2 = None):
    # Test the custom defined python function
    dataframe1 = my_func(dataframe1)

    # Test to read custom uploaded files by relative path
    with open('./Script Bundle/my_sample.txt', 'r') as text_file:
        sample = text_file.read()
    return dataframe1, pd.DataFrame(columns=["Sample"], data=[[sample]])
"""
    # pylint: disable=no-value-for-parameter
    result_dt1, result_dt2 = ExecutePythonScriptModule.run(
        dataset1=input_data_table_1,
        dataset2=input_data_table_2,
        bundle_file=ZipFileWrapper(bundle_zip_path),
        python_stream_reader=script
    )

    assert result_dt1.data_frame.equals(input_data_table_1.data_frame)
    assert result_dt2.data_frame.equals(pd.DataFrame(columns=["Sample"], data=[[custom_sample]]))


@pytest.mark.parametrize(
    "except_script, target_error_message", [
        ("""
import pandas as pd

# Invalid function name
def any_other_func(dataframe1 = None, dataframe2 = None):

    return dataframe1,
""", "has no attribute 'azureml_main'"),
        ("""
import pandas as pd

# Too many parameters
def azureml_main(dataframe1, dataframe2, dataframe3):

    return dataframe1,
""", "missing 1 required positional argument"), ])
def test_execute_python_script_throw_exception(except_script, target_error_message):
    with pytest.raises(FailedToEvaluateScriptError) as error_info:
        # pylint: disable=no-value-for-parameter
        ExecutePythonScriptModule.run(
            dataset1=DataTable(),
            python_stream_reader=except_script
        )
    assert target_error_message in str(error_info.value)


def test_execute_python_script_with_data_table_has_iterable_element():
    python_script = """
import pandas as pd
import numpy as np

# The entry point function can contain up to two input arguments:
#   Param<dataframe1>: a pandas.DataFrame
#   Param<dataframe2>: a pandas.DataFrame
def azureml_main(dataframe1 = None, dataframe2 = None):

    # Execution logic goes here
    dataframe1['col0'] = [[1, 2], [3, 4]]
    dataframe1['col1'] = [pd.Series([1, 2]), pd.Series([3, 4])]
    dataframe1['col2'] = [np.array([1, 2]), np.array([3, 4])]
    dataframe1['col3'] = [{'apple': 1}, {'banana': 2}]
    dataframe1['col4'] = [pd.DataFrame({'a': [1]}), pd.DataFrame({'b': [2]})]


    # If a zip file is connected to the third input port,
    # it is unzipped under "./Script Bundle". This directory is added
    # to sys.path. Therefore, if your zip file contains a Python file
    # mymodule.py you can import it using:
    # import mymodule

    # Return value must be of a sequence of pandas.DataFrame
    # E.g.
    #   -  Single return value: return dataframe1,
    #   -  Two return values: return dataframe1, dataframe2
    return dataframe1,
"""

    dt = DataTable(pd.DataFrame(columns=['col0', 'col1', 'col2', 'col3', 'col4']))
    # pylint: disable=no-value-for-parameter
    compute_dt = ExecutePythonScriptModule.run(
        dataset1=dt,
        python_stream_reader=python_script
    )[0]
    expect_df = pd.DataFrame(columns=['col0', 'col1', 'col2', 'col3', 'col4'])
    expect_df['col0'] = [[1, 2], [3, 4]]
    expect_df['col1'] = [pd.Series([1, 2]), pd.Series([3, 4])]
    expect_df['col2'] = [np.array([1, 2]), np.array([3, 4])]
    expect_df['col3'] = [{'apple': 1}, {'banana': 2}]
    expect_df['col4'] = [pd.DataFrame({'a': [1]}), pd.DataFrame({'b': [2]})]
    for index in range(compute_dt.data_frame.shape[1]):
        for column in range(compute_dt.data_frame.shape[0]):
            try:
                assert compute_dt.data_frame.iloc[column, index] == expect_df.iloc[column, index]
            except Exception:
                assert all(compute_dt.data_frame.iloc[column, index] == expect_df.iloc[column, index])


@pytest.mark.parametrize(
    "python_script, expect_error_message", [
        ("""
import pandas as pd

def azureml_main(dataframe1 = None, dataframe2 = None):
    dataframe1 = pd.DataFrame({1: [1]})

    return dataframe1,
""", "Column names: [[]1[]] are not string"),  # return tuple
        ("""
import pandas as pd

def azureml_main(dataframe1 = None, dataframe2 = None):
    dataframe1 = pd.DataFrame({1: [1]})

    return dataframe1
""", "Column names: [[]1[]] are not string"),  # return pd.DataFrame
    ]
)
def test_execute_python_script_verify_column_names_are_string(python_script, expect_error_message):
    with pytest.raises(FailedToEvaluateScriptError, match=rf".*{expect_error_message}.*"):
        # pylint: disable=no-value-for-parameter
        ExecutePythonScriptModule.run(
            dataset1=DataTable(),
            python_stream_reader=python_script
        )
