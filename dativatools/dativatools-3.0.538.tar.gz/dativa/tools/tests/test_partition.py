import logging
import unittest
import os
import pandas as pd
import shutil
from pandas.testing import assert_frame_equal
from dativa.tools.pandas import ParquetHandler
from dativa.tools.pandas import CSVHandler
from dativa.tools.pandas import athena_partition

logger = logging.getLogger("dativa.tools.athena_partition.tests")


class PartitionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df = pd.DataFrame({"col1": [1, 2, 3, 4, 5, 1, "4", 3, 4, "4", "4", 4, 2, 3, "4"],
                               "col2": [6, 7, 8, 9, 10, 5, 6, 7, 5, "10", 7, 6, 8, 7, 6],
                               "col3": [11, 12, 13, 14, 15, "a", "b", "y", 1, 3, 15, 66, 77, 13, 16],
                               "col4": ["sda", "", 16, "17", 18, "14", 12, 13, 14, 5, 6, 45, 34, 76, 87]}).astype(
            {"col4": str, "col2": int, "col3": str})
        try:
            os.mkdir(os.path.join(os.path.dirname(__file__), "test_data/athena_partition/output"))
        except FileExistsError:
            pass
        cls.base_path = os.path.join(os.path.dirname(__file__), "test_data/athena_partition/output")



    def test_csv_out(self):
        expected_data = os.path.join(os.path.dirname(__file__), "test_data/athena_partition/expected_csv.csv")
        for file in os.listdir(self.base_path):
            if not file.startswith('.'):
                file_path = os.path.join(self.base_path, file)
                shutil.rmtree(file_path)

        csv = CSVHandler(base_path=self.base_path)
        partition_cat = ["col1"]
        cols_keep = ["col2", "col4"]
        output_data_path = os.path.join(self.base_path, "col1=4")
        paths = athena_partition(self.df, partition_cat, csv, ".csv", cols_keep, name="test_name_",
                                 partition_dtypes=[int])
        self.assertEqual(1, len([name for name in os.listdir(output_data_path)]))
        csv = CSVHandler()
        expected = csv.load_df(expected_data)
        output = csv.load_df(os.path.join(output_data_path, *os.listdir(output_data_path)))

        assert_frame_equal(expected, output, check_like=True)

        for file in os.listdir(self.base_path):
            if not file.startswith('.'):
                file_path = os.path.join(self.base_path, file)
                shutil.rmtree(file_path)

    def test_pq_out(self):
        expected_data = os.path.join(os.path.dirname(__file__), "test_data/athena_partition/expected_parquet.parquet")
        for file in os.listdir(self.base_path):
            if not file.startswith('.'):
                file_path = os.path.join(self.base_path, file)
                shutil.rmtree(file_path)

        pq = ParquetHandler(base_path=self.base_path)
        partition_cat = ["col1"]
        cols_keep = ["col2", "col4"]
        output_data_path = os.path.join(self.base_path, "col1=4")

        paths = athena_partition(self.df, partition_cat, pq, ".parquet", cols_keep, name="test_name_",
                                 partition_dtypes=[int])

        pq = ParquetHandler()
        expected = pq.load_df(expected_data)
        output = pq.load_df(os.path.join(output_data_path, *os.listdir(output_data_path)))
        assert_frame_equal(expected, output, check_like=True)

        for file in os.listdir(self.base_path):
            if not file.startswith('.'):
                file_path = os.path.join(self.base_path, file)
                shutil.rmtree(file_path)

    def test_multi_part(self):
        expected_data = os.path.join(os.path.dirname(__file__), "test_data/athena_partition/expected_multi_csv.csv")
        for file in os.listdir(self.base_path):
            if not file.startswith('.'):
                file_path = os.path.join(self.base_path, file)
                shutil.rmtree(file_path)

        csv = CSVHandler(base_path=self.base_path)
        partition_cat = ["col1", "col2"]
        output_data_path = os.path.join(self.base_path, "col1=4/col2=6")
        paths = athena_partition(self.df, partition_cat, csv, ".csv", name="test_name_",
                                 partition_dtypes=[int, int])
        self.assertEqual(5, len([name for name in os.listdir(os.path.join(self.base_path, "col1=4"))]))
        csv = CSVHandler()
        expected = csv.load_df(expected_data)
        output = csv.load_df(os.path.join(output_data_path, *os.listdir(output_data_path)))

        assert_frame_equal(expected, output, check_like=True)

        for file in os.listdir(self.base_path):
            if not file.startswith('.'):
                file_path = os.path.join(self.base_path, file)
                shutil.rmtree(file_path)

    def test_expected_errors(self):
        csv = CSVHandler()
        with self.assertRaises(ValueError):
            athena_partition(self.df, ["col1"], csv, ".parquet",
                             name="test_name_", partition_dtypes=[int])

        csv = CSVHandler(base_path=self.base_path)
        partition_cat = ["col4"]
        with self.assertRaises(ValueError):
            athena_partition(self.df, partition_cat, csv, ".parquet",
                             name="test_name_", partition_dtypes=[str])

        with self.assertRaises(IndexError):
            athena_partition(self.df, ["col3"], csv, ".parquet",
                             columns_to_keep=["col1", "col7"],
                             name="test_name_", partition_dtypes=[int])

        with self.assertRaises(ValueError):
            athena_partition(self.df, ["col3"], csv, ".parquet",
                             name="test_name_", partition_dtypes=[int])
