import os
import tempfile
import datetime
import pytest
import numpy as np
import pandas as pd
from typing import List
from azureml.designer.modules.datatransform.modules.summarize_data_module import SummarizeDataModule
from azureml.designer.modules.datatransform.tools.dataframe_utils import compare_dataframe
from azureml.studio.core.io.data_frame_directory import save_data_frame_to_directory, load_data_frame_from_directory
from azureml.studio.core.data_frame_schema import DataFrameSchema

EXPECT_COLUMNS = ["Feature","Count","Unique Value Count","Missing Value Count","Min","Max","Mean","Mean Deviation","1st quantile","Median","3rd quantile","Mode","Range","Sample Variance","Sample Standard Deviation","Sample Skewness","Sample Kurtosis","P0.5","P1","P5","P95","P99","P99.5"]

def test_string_column():
    input_data = pd.DataFrame(["A", "B", "A", "C", "A"], columns = ["Col1"])
    expect_output = create_expect_output([
        {"Feature": "Col1", "Count": np.int64(5), "Unique Value Count" : np.int64(3), "Missing Value Count": 0, "Mode":"A"}
        ])
    assert summarize_data_module_test_kernal(input_data, expect_output)

def test_datetime_column():
    input_data = pd.DataFrame([datetime.datetime(2020, 1, 1), datetime.datetime(2020, 1, 1), datetime.datetime(2020, 1, 1), datetime.datetime(2020, 2, 1), datetime.datetime(2020, 3, 1)], columns = ["Col1"])
    expect_output = create_expect_output([{
        "Feature": "Col1", 
        "Count": np.int64(5), 
        "Unique Value Count" : np.int64(3), 
        "Missing Value Count": 0, 
        "Min":datetime.datetime(2020,1,1),
        "Max":datetime.datetime(2020,3,1),
        "Mean":datetime.datetime(2020,1,19,4,48),
        "1st quantile":datetime.datetime(2020,1,1),
        "Median":datetime.datetime(2020,1,1),
        "3rd quantile":datetime.datetime(2020,2,1),
        "Mode":"2020-01-01 00:00:00",
        "Sample Skewness":1.21459,
        "Sample Kurtosis":0.0798917,
        "P0.5":datetime.datetime(2020,1,1),
        "P1":datetime.datetime(2020,1,1),
        "P5":datetime.datetime(2020,1,1),
        "P95":datetime.datetime(2020,2,24,4,48),
        "P99":datetime.datetime(2020,2,28,20,9,36),
        "P99.5":datetime.datetime(2020,2,29,10,4,48),
        }])
    assert summarize_data_module_test_kernal(input_data, expect_output)


def test_base1():
    input_data = pd.DataFrame([
        [2,0.1, "dog", True],
        [3,0.1, "cat", False],
        [4,0.2, "rabit", True],
        [5,0.1, "dog", False],
    ],columns = ['int','float','str','boolean'])
    assert summarize_data_module_test_kernal(input_data) is True


def test_bool():
    input_data = pd.DataFrame([
        [True],
        [False],
        [True],
        [False],
    ],columns = ['boolean'])
    assert summarize_data_module_test_kernal(input_data) is True

def test_int():
    input_data = pd.DataFrame([
        [2],
        [3],
        [4],
        [5],
    ],columns = ['int'])
    assert summarize_data_module_test_kernal(input_data) is True

def test_float():
    input_data = pd.DataFrame([
        [0.1],
        [0.2],
        [0.3],
        [0.5],
    ],columns = ['float'])
    assert summarize_data_module_test_kernal(input_data) is True

def test_string():
    input_data = pd.DataFrame([
        ['a'],
        ['b'],
        ['c'],
        ['a'],
    ],columns = ['string'])
    assert summarize_data_module_test_kernal(input_data) is True


def test_mix():
    input_data = pd.DataFrame([
        [2,0.1, "dog", datetime.datetime(2020, 1, 1), datetime.datetime(2020, 1, 1)],
        [3,0.1, "cat", datetime.datetime(2020, 1, 1), datetime.datetime(2020, 1, 1)],
        [4,0.2, "rabit", datetime.datetime(2020, 2, 1), datetime.datetime(2020, 1, 1)],
        [5,0.1, "dog", datetime.datetime(2020, 3, 1), datetime.datetime(2020, 1, 1)],
    ], columns=['int','float','string','datetime','datetime2'])
    assert summarize_data_module_test_kernal(input_data) is True

def create_expect_output(data:List[dict]):
    columns = [ key for key in EXPECT_COLUMNS]
    data = [[row[key] if  key in row else None for key in columns] for row in data]
    output = pd.DataFrame(data, columns=columns)
    output = output.astype({'Count': 'int64'})
    return output

def summarize_data_module_test_kernal(
        input_data: pd.DataFrame,
        expect_table: pd.DataFrame = None
) -> bool:
    with tempfile.TemporaryDirectory(dir='./') as tmpdirname:
        input_path = os.path.join(tmpdirname, 'input//')
        # os.makedirs(os.path.dirname(input_path))
        # input_data.to_parquet(input_path)
        schema = DataFrameSchema.data_frame_to_dict(input_data)
        save_data_frame_to_directory(input_path, data=input_data, schema=schema)
        output_path = os.path.join(tmpdirname, 'output//')
        module = SummarizeDataModule()
        module.insert_arguments(**({
            'input': os.path.dirname(input_path),
            'dataset': os.path.dirname(output_path)}))
        module.train()
        result = load_data_frame_from_directory(output_path).data
        # result = pd.read_parquet(output_path)
        print("-"*60)
        print("Result table.T:")
        print(result.T)
        print(result.dtypes)
        if expect_table is None:
            return True
        print("-"*60)
        print("Expected table.T:")
        print(expect_table.T)
        print(expect_table.dtypes)
        return compare_dataframe(result, expect_table)