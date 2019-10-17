import os
import pytest

import pandas as pd

from azureml.studio.modulehost.handler.port_io_handler import InputHandler
from azureml.studio.common.datatable.data_table import DataTable
from azureml.studio.core.io.data_frame_directory import save_data_frame_to_directory
from azureml.studio.modulehost.handler.sidecar_files import DataFrameSchemaDumper


INPUT_FILE_NAMES = [
    'input0.ilearner',
    'input0.data.ilearner',
    'input0.alghost.ilearner',
    'input0.nh.ilearner',
    'data.dataset.parquet',
    'data.csv.dataset.parquet',
    'alghost.csv',
    'alghost.dataset.csv'
]


def test_handle_input_from_file_name_without_data_type():
    for input_file_name in INPUT_FILE_NAMES:
        full_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'input', input_file_name)
        assert InputHandler.handle_input_from_file_name(full_file_path)


@pytest.mark.parametrize(
    'file_name, file_type', [
        ('dummpy_file.ilearner', 'Learner'),
        ('dummpy_file.itransform', 'Transform'),
        ('dummpy_file.icluster', 'Cluster')
    ]
)
def test_file_not_exist_error_for_itransform_and_ilearner(file_name, file_type):
    detail_message = f'Please check the train experiment which generates the {file_type} file ' + \
                    f'has been deleted or not. If deleted, please re-generate and save the {file_type} file.'
    with pytest.raises(FileNotFoundError, match=f'File: "{file_name}" does not exist: {detail_message}'):
        InputHandler.handle_input_from_file_name(file_name)


def test_data_table_input_with_schema(tmp_path):
    dt = DataTable(pd.DataFrame({'aaa': ['c', 'd', 'a', 'b'], 'bbb': [1, 2, 3, 4]}))
    schema = DataFrameSchemaDumper(dt).dump_to_dict()
    save_data_frame_to_directory(tmp_path, dt.data_frame, schema=schema)
    result = InputHandler.handle_input_directory(tmp_path)
    assert isinstance(result, DataTable)
    assert schema == DataFrameSchemaDumper(result).dump_to_dict()


def test_data_table_input_from_data_frame_directory():
    dfd_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'input/data_frame_directory')
    dt = InputHandler.handle_input_directory(dfd_path)
    assert dt.number_of_rows != 0
