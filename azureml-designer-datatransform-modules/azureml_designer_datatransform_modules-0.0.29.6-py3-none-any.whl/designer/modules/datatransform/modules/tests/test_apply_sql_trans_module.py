import tempfile
import os
import datetime
import random
import pytz
import pytest
import pandas as pd
from azureml.designer.modules.datatransform.tools.sample_data_gen import gen_empty_table, convert_csv
from azureml.designer.modules.datatransform.modules.apply_sql_trans_module import ApplySqlTransModule
from azureml.designer.modules.datatransform.tools.dataframe_utils import compare_dataframe
from azureml.studio.core.io.data_frame_directory import save_data_frame_to_directory, load_data_frame_from_directory
from azureml.studio.core.data_frame_schema import DataFrameSchema
from azureml.studio.internal.error import InvalidSQLScriptError
def test_empty_table():
    empty_table = gen_empty_table({"ID": "int", "Age": "int"})
    query = "select * from t1"
    expect_table = gen_empty_table({"ID": "object", "Age": "object"})
    print(os.sys.path)
    assert apply_sql_trans_module_test_kernal(table1=empty_table, query=query, expect_table=expect_table) is True

def test_join_table():
    t1 = pd.DataFrame([[1],[2],[3]], columns=["col1"])
    t2 = pd.DataFrame([[2],[3],[4]], columns=["c1"])
    query = 'SELECT t1.*, t2.* FROM t1 LEFT OUTER JOIN t2 ON t1.col1 = t2.c1'
    assert apply_sql_trans_module_test_kernal(table1=t1, table2=t2, expect_table=None, query=query) is True

def test_null_character_in_customer_script():
    data = [[datetime.datetime(2016, 11, 2, 16, 49, 44), 55, 1973, "MASTERS_DEGREE",
             8, 5, "\u0000", 0, 0, 0, 0, 3, -1, 0, 0, 0, 1,
             0, 0, 2, 2, "MI", 48221, datetime.datetime(2016, 11, 2, 16, 49, 45), 28, 6, 0, 0, 0, 0, 0]]
    columns = ["CreateDateProfile", "AgeProfile", "GraduationYear", "DegreeTypeProfile", "CreditsEarned",
               "LevelOfEducation", "Salutation", "ComputerAccess", "EmploymentStatus", "Language", "Military",
               "CampusType", "PlanToStart", "Salary", "SchoolStatus", "TimeToCommit", "UsCitizen",
               "WorkExperience", "CreditsOutsideUs", "LicensedRn", "LicenseLpn", "State", "Zip",
               "CreateDateScore", "TargusEduRollup", "ResultCode", "GCU_Preping", "CEC_Preping", "Argosy_PrePing",
               "UMA_Preping", "UMA_PrePIng_isValid"]
    t1 = pd.DataFrame(data, columns=columns)
    t2 = convert_csv('./azureml/designer/modules/datatransform/testdata/codes.csv')
    query = 'SELECT t1.*, t2.City, t2.County \r\nFROM t1\r\nLEFT OUTER JOIN t2 ON RTrim(t1.zip) = RTrim(t2.zip) ;\r\n'
    assert apply_sql_trans_module_test_kernal(table1=t1, table2=t2, expect_table=None, query=query) is True


# @pytest.mark.skip(reason="no way to catch this warning")
def test_malicious_sql():
    data = [[float(8), 4, "10"],
            [float(2), 9, "13"],
            [float(7), 1, "green"]]
    columns = ["A", "B", "C"]
    t1 = pd.DataFrame(data, columns=columns)
    query = "select * from T1; .shell del c:\\temp\\sqlitetest.txt"
    with pytest.raises(InvalidSQLScriptError):
        apply_sql_trans_module_test_kernal(table1=t1, expect_table=None, query=query)


def test_malicious_sql2():
    data = [[float(8), 4, "10"],
            [float(2), 9, "13"],
            [float(7), 1, "green"]]
    columns = ["A", "B", "C"]
    t1 = pd.DataFrame(data, columns=columns)
    query = "select * from T3;"
    with pytest.raises(InvalidSQLScriptError):
        apply_sql_trans_module_test_kernal(table1=t1, expect_table=None, query=query)

def test_basic1():
    data = [[float(8), 4, "10"],
            [float(2), 9, "13"],
            [float(7), 1, "green"]]
    columns = ["A", "B", "C"]
    t1 = pd.DataFrame(data, columns=columns)
    query = "select * from t1;"
    assert apply_sql_trans_module_test_kernal(table1=t1, expect_table=t1, query=query) is True


def test_basic_time_month():
    t1 = pd.DataFrame([
        [
        random_datetime(datetime.datetime(1970, 1, 1, 0, 0, 0, tzinfo=pytz.UTC), datetime.datetime.utcnow().replace(tzinfo=pytz.utc)),
        None if i % 2 == 0 else random_datetime(datetime.datetime(1970, 1, 1, 0, 0, 0, tzinfo=pytz.UTC), datetime.datetime.utcnow().replace(tzinfo=pytz.utc))] for i in range(0, 10)
        ],
        columns=["Col1", "Col2"])
    expect = t1.copy()
    print(expect.dtypes)
    expect["Col2"] = expect["Col1"].apply((lambda x: datetime.datetime.strftime(x, "%m")))
    query = "select Col1, strftime('%m', Col1) AS Col2 from t1;"
    assert apply_sql_trans_module_test_kernal(table1=t1, expect_table=expect, query=query) is True

# def test_non_col_name():
#     t1 = pd.DataFrame([
#         [1]
#     ])
#     expect = t1.copy()
#     expect.columns = ['T1COL0']
#     query = "select t1.* from t1"
#     assert apply_sql_trans_module_test_kernal(table1=t1, expect_table=expect, query=query) is True

def apply_sql_trans_module_test_kernal(
        table1: pd.DataFrame,
        query: str,
        expect_table: pd.DataFrame,
        table2: pd.DataFrame = None,
        table3: pd.DataFrame = None
        ) -> bool:
    with tempfile.TemporaryDirectory(dir=".") as tmpdirname:
        table1_path = os.path.join(tmpdirname,  't1\\')
        # os.makedirs(os.path.dirname(table1_path))
        # table1.to_parquet(table1_path)
        save_data_frame_to_directory( table1_path, data=table1, schema=DataFrameSchema.data_frame_to_dict(table1))
        table2_path = None
        if not table2 is None:
            table2_path = os.path.join(tmpdirname, 't2\\')
            # os.makedirs(os.path.dirname(table2_path))
            # table2.to_parquet(table2_path)
            save_data_frame_to_directory(table2_path, data=table2, schema=DataFrameSchema.data_frame_to_dict(table2))
        table3_path = None
        if not table3 is None:
            table3_path = os.path.join(tmpdirname, 't3\\')
            # os.makedirs(os.path.dirname(table3_path))
            # table3.to_parquet(table3_path)
            save_data_frame_to_directory(table3_path, data=table3, schema=DataFrameSchema.data_frame_to_dict(table3))
        output_path = os.path.join(tmpdirname, 'output\\')
        module = ApplySqlTransModule()
        module.insert_arguments(**({'t1': os.path.dirname(table1_path) , 't2': os.path.dirname(table2_path) if table2_path else None, 't3': os.path.dirname(table3_path) if table3_path else None,
                                    'dataset': os.path.dirname(output_path), 'sqlquery': query}))
        module.train()
        # result = pd.read_parquet(output_path)
        result = load_data_frame_from_directory(output_path).data
        if expect_table is None:
            return True
        return compare_dataframe(result, expect_table)


def random_datetime(start: datetime, end: datetime):
    dt = start + random.random() * (end - start)
    return dt.replace(microsecond=0)
