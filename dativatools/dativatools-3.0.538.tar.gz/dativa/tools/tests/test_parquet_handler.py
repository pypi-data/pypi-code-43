import logging
import unittest
import os
import pandas as pd
from pandas.testing import assert_frame_equal
from dativa.tools.pandas import ParquetHandler
import pyarrow as pa
import numpy as np

logger = logging.getLogger("dativa.parquet_handler.tests")


class ParquetTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        print("Running setup class")
        self.orig_base_path = "{0}/test_data/parquet".format(os.path.dirname(os.path.abspath(__file__)))
        self.parquet_basic = os.path.join(self.orig_base_path, 'data.parquet')

    def _get_parquet_handler(self):
        pq_obj = ParquetHandler()
        return pq_obj

    def _get_parquet_file_row_group(self):
        parquet_file_path = os.path.join(self.orig_base_path, 'data.parquet')
        pq_obj = ParquetHandler(parquet_file_path, 0)
        return pq_obj

    def _get_parquet_file_multiple_row_groups(self):
        parquet_file_path = os.path.join(self.orig_base_path, 'data_row_groups.parquet')
        pq_obj = ParquetHandler(parquet_file_path, 1)
        return pq_obj

    def _get_parquet_file_compression(self):
        parquet_file_path = os.path.join(self.orig_base_path, 'data_gzip.parquet')
        pq_obj = ParquetHandler(parquet_file_path)
        return pq_obj

    def test_load_df(self):
        pq_obj = ParquetHandler()
        df = pq_obj.load_df(self.parquet_basic)
        self.assertTrue(isinstance(df, pd.DataFrame), True)

    def test_load_df_row_groups(self):
        parquet_file_path = os.path.join(self.orig_base_path, 'data_row_groups.parquet')
        pq_obj = ParquetHandler()
        df = pq_obj.load_df(parquet_file_path, read_row_group=0)
        self.assertTrue(isinstance(df, pd.DataFrame), True)

    def test_load_df_cols(self):
        pq_obj = ParquetHandler()
        cols_names = ['registration_dttm', 'id',
                      'first_name', 'last_name', 'gender']
        parquet_file_path = os.path.join(self.orig_base_path, 'data.parquet')
        df = pq_obj.load_df(parquet_file_path, cols_names)
        self.assertTrue(isinstance(df, pd.DataFrame), True)

    def test_load_df_cols_rowgroups(self):
        pq_obj = ParquetHandler()
        parquet_file_path = os.path.join(self.orig_base_path, 'data.parquet')
        cols_names = ['registration_dttm', 'id',
                      'first_name', 'last_name', 'gender']
        df = pq_obj.load_df(parquet_file_path, cols_names, 0)
        self.assertTrue(isinstance(df, pd.DataFrame), True)

    def test_save_df(self):
        pq_obj = ParquetHandler()
        parquet_file_path = os.path.join(self.orig_base_path, 'data.parquet')
        df = pq_obj.load_df(parquet_file_path)
        self.assertIsNone(pq_obj.save_df(df, parquet_file_path))

    def test_save_df_row_group(self):
        parquet_file_path = os.path.join(self.orig_base_path, 'data.parquet')
        pq_obj = ParquetHandler()
        df = pq_obj.load_df(parquet_file_path, read_row_group=0)
        self.assertIsNone(pq_obj.save_df(df, parquet_file_path))

    def test_save_df_compression(self):
        parquet_file_path = os.path.join(self.orig_base_path, 'data_gzip.parquet')
        pq_obj = ParquetHandler()
        df = pq_obj.load_df(parquet_file_path)
        self.assertIsNone(pq_obj.save_df(df, parquet_file_path))

    def test_new_file_write(self):
        parquet_file_path = os.path.join(self.orig_base_path, 'data.parquet')
        pq_obj = ParquetHandler()
        df = pq_obj.load_df(parquet_file_path, read_row_group=0)
        new_file_path = os.path.join(self.orig_base_path, 'new_data.parquet')
        self.assertIsNone(pq_obj.save_df(df, new_file_path))
        os.remove(new_file_path)

    def test_write_from_df(self):
        csv_file_path = os.path.join(self.orig_base_path, 'emails.csv')
        df = pd.read_csv(csv_file_path)
        pq_obj = ParquetHandler()
        new_file_path = os.path.join(self.orig_base_path, 'new_data.parquet')
        self.assertIsNone(pq_obj.save_df(df, new_file_path))
        assert_frame_equal(df, pq_obj.load_df(new_file_path))
        os.remove(new_file_path)

    def test_invalid_base_path(self):
        with self.assertRaises(ValueError):
            ParquetHandler(base_path="some_path_abc/")
        with self.assertRaises(ValueError):
            ParquetHandler(row_group_size=-2)
        with self.assertRaises(ValueError):
            ParquetHandler(use_dictionary='Yes')
        with self.assertRaises(ValueError):
            ParquetHandler(use_deprecated_int96_timestamps='Yes')
        with self.assertRaises(ValueError):
            ParquetHandler(coerce_timestamps='Yes')
        with self.assertRaises(ValueError):
            ParquetHandler(compression='zip')

    def test_read_from_s3(self):
        s3_path = "s3://07092018pqtest/data.parquet"
        pq_obj = ParquetHandler()
        df = pq_obj.load_df(self.parquet_basic)
        pq_obj.save_df(df, s3_path)
        reload_df = pq_obj.load_df(s3_path)
        assert_frame_equal(df, reload_df)

    def test_s3_base_path(self):
        s3_path = "s3://07092018pqtest/data.parquet"
        pq_obj = ParquetHandler(base_path=s3_path)
        self.assertEqual(s3_path, pq_obj.base_path)

    def test_pq_schema_int64(self):
        new_file_path = os.path.join(self.orig_base_path, 'new_data.parquet')
        test_df = pd.DataFrame(
            {"col1": [1, 2, 3, 4, 5], "col2": ["a", "s", "6", "7", "t"]})
        fields = [
            pa.field("col1", pa.int64()),
            pa.field("col2", pa.string())
        ]
        my_schema = pa.schema(fields)
        pq_obj = ParquetHandler()

        pq_obj.save_df(test_df, new_file_path, schema=my_schema)

        assert_frame_equal(test_df, pq_obj.load_df(new_file_path))
        os.remove(new_file_path)

    def test_pq_schema_int32(self):
        # Tests the down casting of int64 to int32 without explicit conversion
        new_file_path = os.path.join(self.orig_base_path, 'new_data.parquet')
        test_df = pd.DataFrame(
            {"col1": [1, 2, 3, 4, 128], "col2": ["a", "s", "6", "7", "t"]})
        fields = [
            pa.field("col1", pa.int32()),
            pa.field("col2", pa.string())
        ]
        test_df = test_df.astype({"col1": np.int32})
        my_schema = pa.schema(fields)
        pq_obj = ParquetHandler()

        pq_obj.save_df(test_df, new_file_path, schema=my_schema)

        assert_frame_equal(test_df, pq_obj.load_df(new_file_path))
        os.remove(new_file_path)

    def test_pq_schema_date_time(self):

        new_file_path = os.path.join(self.orig_base_path, 'new_data.parquet')
        rng = pd.date_range('2015-02-24', periods=5, freq='23H')
        test_df = pd.DataFrame({'Date': rng, 'Val': np.random.randn(len(rng))})

        test_df['Date'] = pd.to_datetime(test_df['Date'], unit='D')
        fields = [
            pa.field("Date", pa.timestamp('ms')),
            pa.field("Val", pa.float64())
        ]
        my_schema = pa.schema(fields)
        pq_obj = ParquetHandler()

        pq_obj.save_df(test_df, new_file_path, schema=my_schema)
        assert_frame_equal(test_df, pq_obj.load_df(new_file_path))
        os.remove(new_file_path)

    def test_pq_schema_as_dict(self):

        new_file_path = os.path.join(self.orig_base_path, 'new_data.parquet')
        pq_obj = ParquetHandler()

        # dict for all columns
        test_df = pd.DataFrame({'Truth': [1, 0]})
        expected_df = pd.DataFrame({'Truth': [True, False]})

        pq_obj.save_df(test_df, new_file_path, schema={'Truth': bool})
        assert_frame_equal(expected_df, pq_obj.load_df(new_file_path))

        # dict for some columns, infer the rest
        test_df = pd.DataFrame({'Truth': [1, 0], 'Falacy': [0, 1]})
        expected_df = pd.DataFrame({'Truth': [True, False], 'Falacy': [0, 1]})

        pq_obj.save_df(test_df, new_file_path, schema={'Truth': bool}, infer_other_dtypes=True)
        assert_frame_equal(expected_df, pq_obj.load_df(new_file_path))

        # empty dict, should just infer all columns
        test_df = pd.DataFrame({'Truth': [1, 0], 'Falacy': [0, 1]})
        expected_df = pd.DataFrame({'Truth': [1, 0], 'Falacy': [0, 1]})

        pq_obj.save_df(test_df, new_file_path, schema={})
        assert_frame_equal(expected_df, pq_obj.load_df(new_file_path))


        os.remove(new_file_path)

    def test_pq_schema_as_schema(self):

        new_file_path = os.path.join(self.orig_base_path, 'new_data.parquet')
        pq_obj = ParquetHandler()

        # schema for all columns
        test_df = pd.DataFrame({'Truth': [1, 0]})
        expected_df = pd.DataFrame({'Truth': [True, False]})

        pq_obj.save_df(test_df, new_file_path,
            schema=pa.lib.schema(
                [
                    pa.field('Truth', pa.bool_()),
                ]
            )
        )
        assert_frame_equal(expected_df, pq_obj.load_df(new_file_path))

        # schema for some columns, infer the rest
        test_df = pd.DataFrame({'Truth': [1, 0], 'Falacy': [0, 1]})
        expected_df = pd.DataFrame({'Truth': [True, False], 'Falacy': [0, 1]})

        pq_obj.save_df(test_df, new_file_path,
                       schema=pa.lib.schema(
                           [
                               pa.field('Truth', pa.bool_()),
                           ]
                       ), infer_other_dtypes=True
                       )
        assert_frame_equal(expected_df, pq_obj.load_df(new_file_path))

        # empty schema, should just infer all columns
        test_df = pd.DataFrame({'Truth': [1, 0], 'Falacy': [0, 1]})
        expected_df = pd.DataFrame({'Truth': [1, 0], 'Falacy': [0, 1]})

        pq_obj.save_df(test_df, new_file_path, schema=pa.lib.schema([]))
        assert_frame_equal(expected_df, pq_obj.load_df(new_file_path))


        os.remove(new_file_path)

    def test_invalid_schema_inputs(self):

        new_file_path = os.path.join(self.orig_base_path, 'new_data.parquet')
        test_df = pd.DataFrame({'Truth': [1, True], 'non-supported_col_type': [ParquetHandler, ParquetHandler]})
        pq_obj = ParquetHandler()

        with self.assertRaises(NotImplementedError):
            # types not supported in schema passed as dict
            pq_obj.save_df(test_df, new_file_path, schema={'Truth': ParquetHandler})
        with self.assertRaises(NotImplementedError):
            # columns with multiple dtypes
            pq_obj.save_df(test_df, new_file_path)
        with self.assertRaises(NotImplementedError):
            # types not supported for column dtypes in schema passed as dict
            pq_obj.save_df(test_df, new_file_path, schema={'Truth': bool}, infer_other_dtypes=True)
        with self.assertRaises(NotImplementedError):
            # types not supported for column dtypes in schema passed as schema
            pq_obj.save_df(test_df, new_file_path, schema=pa.lib.schema([pa.field('Truth', pa.bool_())]),
                           infer_other_dtypes=True)
        with self.assertRaises(TypeError):
            # schema should be dict or pyarrow.lib.Schema
            pq_obj.save_df(test_df, new_file_path, schema=[('Truth', ParquetHandler)])
        with self.assertRaises(ValueError):
            # columns specified in schema passed as dict but not in dataframe
            pq_obj.save_df(test_df, new_file_path, schema={'Falacy': bool})
        with self.assertRaises(ValueError):
            # columns specified in schema passed as schema but not in dataframe
            pq_obj.save_df(test_df, new_file_path, schema=pa.lib.schema([pa.field('Falacy', pa.bool_())]))
        with self.assertRaises(ValueError):
            # schema passed as dict with not all columns specified, infer_other_dtypes not specified
            pq_obj.save_df(test_df, new_file_path, schema={'Truth': bool})
        with self.assertRaises(ValueError):
            # schema passed as dict with not all columns specified, infer_other_dtypes specified
            pq_obj.save_df(test_df, new_file_path, schema={'Truth': bool}, infer_other_dtypes=False)
        with self.assertRaises(ValueError):
            # schema passed as schema with not all columns specified, infer_other_dtypes not specified
            pq_obj.save_df(test_df, new_file_path, schema=pa.lib.schema([pa.field('Truth', pa.bool_())]))
        with self.assertRaises(ValueError):
            # schema passed as schema with not all columns specified, infer_other_dtypes specified
            pq_obj.save_df(test_df, new_file_path, schema=pa.lib.schema([pa.field('Truth', pa.bool_())]),
                           infer_other_dtypes=False)

    def test_missing_data(self):

        new_file_path = os.path.join(self.orig_base_path, 'new_data.parquet')
        pq_obj = ParquetHandler()

        test_df = pd.DataFrame({
            'int_col': [1, pd.np.nan],
            'to_str_col': [463, pd.np.nan],
            'str_col': [pd.np.nan, 'a string'],
        })
        expected_df = pd.DataFrame({
            'int_col': [1, pd.np.nan],
            'to_str_col': ['463.0', pd.np.nan],
            'str_col': [pd.np.nan, 'a string'],
        })

        pq_obj.save_df(test_df, new_file_path, schema={'to_str_col': str}, infer_other_dtypes=True)
        assert_frame_equal(expected_df, pq_obj.load_df(new_file_path))

        os.remove(new_file_path)
