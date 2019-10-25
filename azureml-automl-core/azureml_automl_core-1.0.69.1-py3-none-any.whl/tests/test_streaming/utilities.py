# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Utilties for streaming unit tests."""
import tempfile

import pandas as pd


def dataframe_as_csv_file(dataframe: pd.DataFrame) -> str:
    """
    Writes the pandas dataframe as a csv temp file

    :param dataframe: data to write into the csv file
    :return: path to the generated csv file
    """
    temp_file = tempfile.NamedTemporaryFile(prefix='_test_streaming', suffix='.csv', delete=False)
    path = temp_file.name
    temp_file.close()
    dataframe.to_csv(path_or_buf=path, index=False)
    return path
