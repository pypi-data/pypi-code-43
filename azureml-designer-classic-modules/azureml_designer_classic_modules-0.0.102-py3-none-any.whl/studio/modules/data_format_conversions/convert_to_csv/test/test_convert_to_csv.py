import os
import pytest
import pandas as pd
import numpy as np

from azureml.studio.modulehost.handler.port_io_handler import OutputHandler, InputHandler
from azureml.studio.modules.data_format_conversions.convert_to_csv.convert_to_csv \
    import ConvertToCSVModule
from azureml.studio.common.datatable.data_table import DataTable
from azureml.studio.modulehost.module_reflector import RETURN_KEY
from azureml.studio.modulehost.attributes import DataTableOutputPort


def script_directory():
    return os.path.dirname(os.path.abspath(__file__))


def validate_data_table(compute_dt, expect_dt):
    assert compute_dt.data_frame.equals(expect_dt.data_frame)
    assert compute_dt.meta_data.column_attributes == expect_dt.meta_data.column_attributes


@pytest.fixture
def data_type():
    return_annotations = ConvertToCSVModule.run.__annotations__[RETURN_KEY]
    output_port = next(filter(lambda annotation: isinstance(annotation, DataTableOutputPort), return_annotations))
    return output_port.return_type


@pytest.fixture
def data_table():
    df = pd.DataFrame()
    df['col0'] = [2, 1, 10]
    df['col1'] = [np.nan, 1.6, 1]
    df['col2'] = [None, 'a', 'b']
    df['col3'] = [np.nan, True, False]
    df['col4'] = [np.nan, np.nan, None]
    return DataTable(df)


@pytest.fixture
def data_table_with_large_row_number():
    df = pd.DataFrame()
    df['col0'] = list(range(100000))
    return DataTable(df)


def test_run(data_table, data_type):

    compute_data_table = ConvertToCSVModule.run(dt=data_table)[0]

    assert compute_data_table is not data_table

    file_path = os.path.join(script_directory(), 'gen')
    os.makedirs(file_path, exist_ok=True)
    file_name = 'Result_dataset.csv'
    OutputHandler.handle_output(compute_data_table, file_path, file_name, data_type)
    data_table_from_csv = InputHandler.handle_input(file_path, file_name, data_type)

    validate_data_table(data_table, data_table_from_csv)


def test_run_with_large_row_number(data_table_with_large_row_number, data_type):
    compute_data_table = ConvertToCSVModule.run(dt=data_table_with_large_row_number)[0]

    file_path = os.path.join(script_directory(), 'gen')
    os.makedirs(file_path, exist_ok=True)
    file_name = 'Result_dataset_with_large_row_number.csv'
    OutputHandler.handle_output(compute_data_table, file_path, file_name, data_type)
    data_table_from_csv = InputHandler.handle_input(file_path, file_name, data_type)
    validate_data_table(data_table_with_large_row_number, data_table_from_csv)
