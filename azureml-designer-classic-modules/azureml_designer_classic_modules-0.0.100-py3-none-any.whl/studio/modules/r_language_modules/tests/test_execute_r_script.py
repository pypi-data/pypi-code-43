import pandas as pd
import numpy as np

import pytest

from azureml.studio.common.datatable.data_table import DataTable
from azureml.studio.common.error import FailedToEvaluateScriptError
from azureml.studio.common.io.data_table_io import data_frame_from_parquet
from azureml.studio.common.zip_wrapper import ZipFileWrapper
from azureml.studio.modules.r_language_modules.execute_r_script import ExecuteRScriptModule, ExecuteRScriptRVersion


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
azureml_main <- function(dataframe1, dataframe2){
  # Recommended output as a Named List
  return(list(dataset1=dataframe1, dataset2=dataframe2))
}
"""),
        ("""
azureml_main <- function(dataframe1, dataframe2){
  # Recommended output as a Named List
  return(list(dataset1=dataframe1))
}
"""),
        ("""
azureml_main <- function(dataframe1, dataframe2){
  # Accepted output - one dataframe only
  return(dataframe1)
}
""")])
def test_execute_r_script(input_data_table_1, input_data_table_2, script):
    # pylint: disable=no-value-for-parameter
    result = ExecuteRScriptModule.run(
        dataset1=input_data_table_1,
        dataset2=input_data_table_2,
        r_stream_reader=script,
        r_lib_version=ExecuteRScriptRVersion.R351
    )[0]

    assert pd.np.array_equal(result.data_frame.values, input_data_table_1.data_frame.values)

    # Ensure the index type is integer rather than string
    assert all(np.issubdtype(idx, np.integer) for idx in result.data_frame.index.values)


@pytest.mark.parametrize(
    "input_data_set_1, input_data_set_2", [
        (DATA_TABLE_1, None),
        (None, DATA_TABLE_2),
        (None, None)])
def test_execute_r_script_empty_input(input_data_set_1, input_data_set_2):
    script = """
    azureml_main <- function(dataframe1, dataframe2){
      # Recommended output as a Named List
      return(list(dataset1=data.frame("A"=0.0)))
    }
    """
    # pylint: disable=no-value-for-parameter
    result = ExecuteRScriptModule.run(
        dataset1=input_data_set_1,
        dataset2=input_data_set_2,
        r_stream_reader=script,
        r_lib_version=ExecuteRScriptRVersion.R351
    )[0]

    assert result.data_frame.equals(pd.DataFrame(columns=["A"], data=[[0.0]]))


@pytest.mark.parametrize(
    "script", [
        ("""
azureml_main <- function(dataframe1, dataframe2){
  # Empty List
  return(list())
}
"""),
        ("""
azureml_main <- function(dataframe1, dataframe2){
  # Empty return
  return()
}
"""),
        ("""
azureml_main <- function(dataframe1, dataframe2){
  # No return
}
""")])
def test_execute_r_script_empty_output(input_data_table_1, input_data_table_2, script):
    # pylint: disable=no-value-for-parameter
    result = ExecuteRScriptModule.run(
        dataset1=input_data_table_1,
        dataset2=input_data_table_2,
        r_stream_reader=script,
        r_lib_version=ExecuteRScriptRVersion.R351
    )

    assert all(x.data_frame.equals(DataTable().data_frame) for x in result)


def test_execute_r_script_with_bundle_zip(tmpdir, input_data_table_1, input_data_table_2):
    import os
    custom_bundle_script = """
my_func <- function(dataset1){
    return(dataset1)
}
"""

    script_file = "my_script.R"
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
source("./Script Bundle/my_script.R")
azureml_main <- function(dataframe1, dataframe2){
    dataframe1 <- my_func(dataframe1)
    sample <- readLines("./Script Bundle/my_sample.txt")
    return (list(dataset1=dataframe1, dataset2=data.frame("Sample"=sample)))
}
"""
    bundle_file = ZipFileWrapper(bundle_zip_path)
    # pylint: disable=no-value-for-parameter
    result_dt1, result_dt2 = ExecuteRScriptModule.run(
        dataset1=input_data_table_1,
        dataset2=input_data_table_2,
        bundle_file=bundle_file,
        r_stream_reader=script,
        r_lib_version=ExecuteRScriptRVersion.R351
    )

    assert pd.np.array_equal(result_dt1.data_frame.values, input_data_table_1.data_frame.values)
    assert result_dt2.data_frame.equals(pd.DataFrame(columns=["Sample"], data=[[custom_sample]]))


@pytest.mark.parametrize(
    "except_script, target_error_message", [
        ("""
# Invalid function name
any_other_func <- function(dataframe1, dataframe2){
  return (list(dataset1=dataframe1))
}
""", 'could not find function \"azureml_main\"'),
        ("""
# Too few parameters
azureml_main <- function(dataframe1){
  return (list(dataset1=dataframe1))
}
""", "unused argument"),
        ("""
# Return invalid data type
azureml_main <- function(dataframe1, dataframe2){
  return (0)
}
""", "Unsupported return type")])
def test_execute_r_script_throw_exception(except_script, target_error_message):
    with pytest.raises(FailedToEvaluateScriptError) as error_info:
        # pylint: disable=no-value-for-parameter
        ExecuteRScriptModule.run(
            dataset1=DataTable(),
            r_stream_reader=except_script,
            r_lib_version=ExecuteRScriptRVersion.R351
        )
    assert target_error_message in str(error_info.value)


def test_execute_r_script_input_data_frame_type(input_data_table_1, input_data_table_2):
    script = """
    azureml_main <- function(dataframe1, dataframe2){
      if (!is.data.frame(dataframe1)) {
        stop(sprintf("Unsupported input type, expect: 'data.frame', actual: '%s'", class(dataframe1)))
      }

      return(list(dataset1=dataframe1))
    }
    """

    # pylint: disable=no-value-for-parameter
    result = ExecuteRScriptModule.run(
        dataset1=input_data_table_1,
        dataset2=input_data_table_2,
        r_stream_reader=script
    )[0]

    assert pd.np.array_equal(result.data_frame.values, input_data_table_1.data_frame.values)


def test_execute_r_script_output_data_frame_type(input_data_table_1, input_data_table_2):
    script = """
    azureml_main <- function(dataframe1, dataframe2){
      r_dataframe <- data.frame("A"=0.0)
      py_dataframe <- r_to_py(r_dataframe)
      if (is.data.frame(py_dataframe)) {
        stop(sprintf("Unexpected type, expect: 'pandas.core.frame.DataFrame', actual: 'data.frame'"))
      }

      return(list(dataset1=r_dataframe, dataset2=py_dataframe))
    }
    """

    # pylint: disable=no-value-for-parameter
    result = ExecuteRScriptModule.run(
        dataset1=input_data_table_1,
        dataset2=input_data_table_2,
        r_stream_reader=script
    )

    assert all(x.data_frame.equals(pd.DataFrame(columns=["A"], data=[[0.0]])) for x in result)


def test_execute_r_script_with_all_data_types_parquet(input_data_table_2):
    script = """
azureml_main <- function(dataframe1, dataframe2){
  # Recommended output as a Named List
  return(list(dataset1=dataframe1))
}
"""

    # Test bug fix: 454419
    # all_types_data.parquet covers all kinds of data type
    # The reason we test it with R script here is R script might be failed in r_to_py method
    # which would convert R types to Python types.
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_parquet = os.path.join(current_dir, "resources/all_types_data.parquet")
    input_data_table_1 = DataTable(data_frame_from_parquet(input_parquet))

    # pylint: disable=no-value-for-parameter
    result = ExecuteRScriptModule.run(
        dataset1=input_data_table_1,
        dataset2=input_data_table_2,
        r_stream_reader=script,
        r_lib_version=ExecuteRScriptRVersion.R351
    )[0]

    assert pd.np.array_equal(result.data_frame.values, input_data_table_1.data_frame.values)
