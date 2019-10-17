import os
import pandas as pd

from azureml.studio.core.utils.fileutils import ExecuteInDirectory

_PARQUET_ENGINE = 'pyarrow'


def data_frame_to_parquet(df: pd.DataFrame, parquet_path):
    # Use chdir to dest_directory to work around the path issue on windows when writing parquet file
    with ExecuteInDirectory(parquet_path) as parquet_file_name:
        # Use len(df.columns)==0 instead of df.empty because df.empty is true when the df has column names but no row.
        # In this case, the column names should be stored.
        if df is not None and not len(df.columns) == 0:
            df.to_parquet(fname=parquet_file_name, engine=_PARQUET_ENGINE,
                          # Fix bug 484283: pyarrow raises error due to the precision problem of timestamps.
                          # Add this option so the nanoseconds will be converted to milliseconds
                          allow_truncated_timestamps=True,
                          )


def data_frame_from_parquet(parquet_path):
    """
    Read pandas DataFrame from parquet file
    :param parquet_path: str
    :return: pd.DataFrame
    """
    # Use chdir to dest_directory to work around the path issue on windows when writing parquet file
    with ExecuteInDirectory(parquet_path) as parquet_file_name:
        if os.path.exists(parquet_file_name):
            return pd.read_parquet(parquet_file_name, engine=_PARQUET_ENGINE)
        else:
            return pd.DataFrame()
