import unittest
import numpy as np
import pandas as pd

from automl.client.core.common.time_series_data_frame import TimeSeriesDataFrame
from azureml.automl.core.featurizer.transformer.timeseries import RestoreDtypesTransformer
from pandas.util.testing import assert_frame_equal, assert_series_equal


class TestRestoreDtypesTransformer(unittest.TestCase):
    """Test different ways of dtype restorations."""

    GRAIN = 'grain'
    DATE = 'date'
    TARGET = 'target_val'

    def setUp(self):
        """Create test data structures."""
        self.data = pd.DataFrame({
            self.DATE: pd.date_range('2001-01-01', freq='W', periods=40),
            self.GRAIN: 'grain',
            'another_date': pd.date_range('2004-01-01', freq='D', periods=40),
            'int_val': np.arange(40),
            'float_val': np.arange(40).astype(float),
            'bool_val': [True, False] * 20,
            'string_val': 'some_text',
            self.TARGET: list(np.arange(30)) + [None] * 10
        }
        )

        unittest.TestCase.setUp(self)

    def _break_dtypes(self, tsdf):
        df = pd.DataFrame(tsdf.copy())
        df.reset_index(drop=False, inplace=True)
        arr = df.values
        df_obj = pd.DataFrame(arr, columns=df.columns)
        assert(all(np.object == val for val in df_obj.dtypes.values))
        return TimeSeriesDataFrame(df_obj,
                                   time_colname=self.DATE,
                                   grain_colnames=self.GRAIN,
                                   ts_value_colname=self.TARGET)

    def _do_test(self, df):
        """Run the actual test."""
        X_train = TimeSeriesDataFrame(df[:30],
                                      time_colname=self.DATE,
                                      grain_colnames=self.GRAIN,
                                      ts_value_colname=self.TARGET)
        X_train_obj = self._break_dtypes(X_train)
        X_test = TimeSeriesDataFrame(df[30:],
                                     time_colname=self.DATE,
                                     grain_colnames=self.GRAIN,
                                     ts_value_colname=self.TARGET)
        X_test_obj = self._break_dtypes(X_test)
        transform = RestoreDtypesTransformer(X_train)
        # Test fit-transform.
        tr = transform.fit_transform(X_train)
        assert_series_equal(tr.dtypes, X_train.dtypes)
        # Test fit and then transform.
        transform = RestoreDtypesTransformer(X_train)
        transform.fit(X_train)
        tr = transform.transform(X_train_obj)
        self._do_check_dtypes(X_train, tr)
        # test set
        tr = transform.transform(X_test_obj)
        self._do_check_dtypes(X_test, tr)

    def _do_check_dtypes(self, tsdf_expected, tsdf_observed):
        """Assertions."""
        for col in tsdf_expected.columns:
            # Skip target column.
            if col == self.TARGET:
                continue
            extype = tsdf_expected[col].dtype
            if all([pd.isnull(val) for val in tsdf_expected[col].values]) or not np.issubdtype(extype, np.number):
                extype = np.object
            if col != self.TARGET:
                self.assertTrue(
                    extype == tsdf_observed[col].dtype,
                    "Incorrect dtype for column {}: {}, expected {}.".format(
                        col,
                        tsdf_observed[col].dtype,
                        extype))
            if all([pd.isnull(val) for val in tsdf_expected[col].values]
                   ) or not np.issubdtype(tsdf_expected[col].dtype, np.number):
                assert_series_equal(tsdf_expected[col].astype(np.object), tsdf_observed[col])
            else:
                assert_series_equal(tsdf_expected[col], tsdf_observed[col])

    def test_restore_dtypes(self):
        """Test dtype restoration on dataframe with no NaNs"""
        self._do_test(self.data)

    def test_all_nans(self):
        """Test dtype restoration on dataframe with all NaNs"""
        self.data['another_date'] = None
        self.data['int_val'] = None
        self.data['float_val'] = None
        self.data['bool_val'] = None
        self.data['string_val'] = None
        self._do_test(self.data)

    def test_some_nans(self):
        """Test dtype restoration on dataframe with some values NaN"""
        self.data['another_date'][0] = None
        self.data['int_val'][1] = None
        self.data['float_val'][2] = None
        self.data['bool_val'][3] = None
        self.data['string_val'][4] = None
        self._do_test(self.data)

    def test_some_cols_nans(self):
        """Test dtype restoration on dataframe with some columns are all NaN"""
        self.data['nan_col'] = None
        self._do_test(self.data)

    def test_sone_cols_and_vals_nan(self):
        """Test dtype restoration on dataframe where some columns are all NaN and some values are NaN"""
        self.data['another_date'][0] = None
        self.data['int_val'][1] = None
        self.data['float_val'][2] = None
        self.data['bool_val'][3] = None
        self.data['string_val'][4] = None
        self.data['nan_col'] = None
        self._do_test(self.data)


if __name__ == '__main__':
    unittest.main()
