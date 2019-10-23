import pandas as pd

from azureml.studio.common.datatable.data_table import DataTable
from azureml.studio.common.datatable.data_table_directory import DataTableDirectory
from azureml.studio.core.data_frame_schema import DataFrameSchema
from azureml.studio.core.io.data_frame_directory import save_data_frame_to_directory


def sample_df():
    return pd.DataFrame({'A': [1, 3, 4], 'B': ['a', 'b', 'c']})


def test_load_from_dfd_raw_df(tmp_path):
    df = sample_df()
    save_data_frame_to_directory(tmp_path, data=df)
    dir_data = DataTableDirectory.load(tmp_path)
    assert isinstance(dir_data.data_table, DataTable)


def test_load_from_dfd_with_schema(tmp_path):
    df = sample_df()
    save_data_frame_to_directory(tmp_path, data=df, schema=DataFrameSchema.data_frame_to_dict(df))
    dir_data = DataTableDirectory.load(tmp_path)
    assert isinstance(dir_data.data_table, DataTable)


def test_load_from_dfd_by_data_table(tmp_path):
    dt = DataTable(df=sample_df())
    save_data_frame_to_directory(tmp_path, data=dt.data_frame, schema=dt.meta_data.to_dict())
    dir_data = DataTableDirectory.load(tmp_path)
    assert dir_data.data_table == dt


def test_reload(tmp_path):
    df = sample_df()
    save_data_frame_to_directory(tmp_path / 'dir1', data=df)
    dir1 = DataTableDirectory.load(tmp_path / 'dir1')

    dir1.dump(tmp_path / 'dir2')
    dir2 = DataTableDirectory.load(tmp_path / 'dir2')
    assert isinstance(dir1.data_table, DataTable) and dir1.data_table == dir2.data_table
