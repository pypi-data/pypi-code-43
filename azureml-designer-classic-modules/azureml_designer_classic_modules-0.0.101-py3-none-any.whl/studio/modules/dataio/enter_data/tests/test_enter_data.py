import numpy as np
import pandas as pd

import pytest

from azureml.studio.modulehost.constants import ColumnTypeName
from azureml.studio.common.io.datatable.data_table_svmlight_reader import DataTableSvmLightReader
from ..enter_data import EnterDataModule, EnterDataDataFormat

SAMPLE_HEADER = ["C1", "C2", "C3"]
SAMPLE_VALUE = ["a", "?", "c"]
EXPECT_DATA_FRAME_NO_HEADER = pd.DataFrame({'Col1': ['a'], 'Col2': [np.nan], 'Col3': ['c']})
EXPECT_DATA_FRAME_HEADER = pd.DataFrame({'C1': ['a'], 'C2': [np.nan], 'C3': ['c']})
COMMA = ","
TAB = "\t"
CRLF = "\n"
ARFF_TEXT = """@relation foo
@attribute width  numeric
@attribute height numeric
@attribute color  {red,green,blue,yellow,black}
@data
5.0,3.25,blue
4.5,3.75,green
3.0,4.00,red
"""
SVMLIGHT_TEXT = """-1 2:1 6:1 18:1 20:1 37:1
+1 5:1 11:1 15:1 32:1 39:1
-1 5:1 16:1 30:1 35:1 41:1
+1 5:1 18:1 19:1 39:1 40:1
-1 2:1 11:1 18:1 20:1 37:1
-1 1:1 6:1 17:1 22:1 36:1
"""


@pytest.fixture
def csv_text():
    return COMMA.join(SAMPLE_VALUE)


@pytest.fixture
def csv_text_with_header():
    return CRLF.join([COMMA.join(SAMPLE_HEADER),
                      COMMA.join(SAMPLE_VALUE)])


@pytest.fixture
def tsv_text():
    return TAB.join(SAMPLE_VALUE)


@pytest.fixture
def tsv_text_with_header():
    return CRLF.join([TAB.join(SAMPLE_HEADER),
                      TAB.join(SAMPLE_VALUE)])


def test_load_csv(csv_text):
    dt = EnterDataModule.run(data_format=EnterDataDataFormat.CSV,
                             data=csv_text,
                             has_header=False)[0]
    assert dt.number_of_rows == 1
    assert dt.column_names == ['Col1', 'Col2', 'Col3']

    assert dt.data_frame.equals(EXPECT_DATA_FRAME_NO_HEADER)


def test_load_csv_with_header(csv_text_with_header):
    dt = EnterDataModule.run(data_format=EnterDataDataFormat.CSV,
                             data=csv_text_with_header,
                             has_header=True)[0]
    assert dt.number_of_rows == 1
    assert dt.data_frame.equals(EXPECT_DATA_FRAME_HEADER)
    assert np.array_equal(dt.column_names, SAMPLE_HEADER)


def test_load_tsv(tsv_text):
    dt = EnterDataModule.run(data_format=EnterDataDataFormat.TSV,
                             data=tsv_text,
                             has_header=False)[0]
    assert dt.number_of_rows == 1
    assert dt.data_frame.equals(EXPECT_DATA_FRAME_NO_HEADER)


def test_load_tsv_with_header(tsv_text_with_header):
    dt = EnterDataModule.run(data_format=EnterDataDataFormat.TSV,
                             data=tsv_text_with_header,
                             has_header=True)[0]
    assert dt.number_of_rows == 1
    assert dt.data_frame.equals(EXPECT_DATA_FRAME_HEADER)
    assert np.array_equal(dt.column_names, SAMPLE_HEADER)


def test_load_arff():
    dt = EnterDataModule.run(data_format=EnterDataDataFormat.ARFF,
                             data=ARFF_TEXT,
                             has_header=False)[0]
    assert dt.number_of_rows == 3
    assert dt.number_of_columns == 3
    assert dt.get_column_type("color") == ColumnTypeName.CATEGORICAL


def test_load_svmlight():
    dt = EnterDataModule.run(data_format=EnterDataDataFormat.SvmLight,
                             data=SVMLIGHT_TEXT,
                             has_header=False)[0]
    assert dt.number_of_rows == 6
    assert dt.number_of_columns == 41 + 1
    assert DataTableSvmLightReader.SVMLIGHT_COLUMN_NAME_LABELS in dt.column_names
