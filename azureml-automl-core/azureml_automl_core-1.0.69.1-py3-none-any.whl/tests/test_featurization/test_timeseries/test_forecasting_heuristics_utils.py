import numpy as np
import pandas as pd
import unittest

from pandas.tseries.frequencies import to_offset

from azureml.automl.core.featurizer.transformer.timeseries.forecasting_heuristic_utils import (
    frequency_based_lags,
    analyze_pacf_one_grain,
    analyze_pacf_per_grain,
    get_heuristic_max_horison,
    get_frequency_safe)

from ...utilities import generate_data_with_lags_and_rw
from automl.client.core.common.exceptions import DataException


class TestForecastingHeuristicUtils(unittest.TestCase):
    """Tests for the heuristic utils."""
    TGT = 'y'
    TIME = 'date'
    SUPPORTED_OFFSETS = [
        'M', 'W', 'W-WED', 'B', 'C', 'MS', 'BM',
        'BMS', 'CBM', 'CBMS', 'Q', 'QS', 'BQ', 'BQS',
        'A', 'AS', 'BYS', 'BA', 'BAS', 'BH', 'CBH', 'D',
        'H', 'T', 'min', 'S', 'BQS-APR',
        'QS-APR', 'Q-APR', 'BAS-NOV', 'AS-NOV', 'A-NOV']

    def test_frequency_based_lags(self):
        """Test the next granularity is detected correctly."""
        # Minute
        # Minutes in hour.
        off = pd.tseries.offsets.Minute(n=1)
        self.assertEqual(frequency_based_lags(off), 60, 'Wrong lag')
        # 90 minute periods in day.
        off = pd.tseries.offsets.Minute(n=90)
        self.assertEqual(frequency_based_lags(off), 16, 'Wrong lag')
        # period undetermined, 0
        off = pd.tseries.offsets.Minute(n=95)
        self.assertEqual(frequency_based_lags(off), 0, 'Wrong lag')

        # Hour
        # Hours in day
        off = pd.tseries.offsets.Hour(n=1)
        self.assertEqual(frequency_based_lags(off), 24, 'Wrong lag')
        # More then a day
        off = pd.tseries.offsets.Hour(n=25)
        self.assertEqual(frequency_based_lags(off), 0, 'Wrong lag')

        # Day
        off = pd.tseries.offsets.Day(n=1)
        self.assertEqual(frequency_based_lags(off), 7, 'Wrong lag')
        off = pd.tseries.offsets.Day(n=2)
        self.assertEqual(frequency_based_lags(off), 0, 'Wrong lag')

        # Month
        off = pd.tseries.offsets.MonthBegin(n=2)
        self.assertEqual(frequency_based_lags(off), 6, 'Wrong lag')
        off = pd.tseries.offsets.MonthEnd(n=5)
        self.assertEqual(frequency_based_lags(off), 0, 'Wrong lag')

        # Quarter
        off = pd.tseries.offsets.QuarterBegin()
        self.assertEqual(frequency_based_lags(off), 4, 'Wrong lag')
        off = pd.tseries.offsets.QuarterEnd(n=2)
        self.assertEqual(frequency_based_lags(off), 2, 'Wrong lag')
        off = pd.tseries.offsets.QuarterEnd(n=3)
        self.assertEqual(frequency_based_lags(off), 0, 'Wrong lag')

        # Year
        off = pd.tseries.offsets.YearBegin(1)
        self.assertEqual(frequency_based_lags(off), 1, 'Wrong lag')
        off = pd.tseries.offsets.YearEnd(15)
        self.assertEqual(frequency_based_lags(off), 0, 'Wrong lag')

    def test_lags_rw(self):
        """Test data if we have both lags and rolling windows."""
        data = generate_data_with_lags_and_rw(
            1, 2,
            TestForecastingHeuristicUtils.TIME,
            TestForecastingHeuristicUtils.TGT)
        data.set_index(TestForecastingHeuristicUtils.TIME, drop=True, inplace=True)
        lag, rw = analyze_pacf_one_grain(data[TestForecastingHeuristicUtils.TGT])
        self.assertEqual(lag, 1, "Wrong lag.")
        self.assertEqual(rw, 2, "Wrong rw.")

    def test_analyze_pacf_one_grain(self):
        """Test test_analyze_pacf_per_grain with lag and rolling window."""
        data = generate_data_with_lags_and_rw(
            1, 2,
            TestForecastingHeuristicUtils.TIME,
            TestForecastingHeuristicUtils.TGT)
        lag, rw = analyze_pacf_per_grain(
            data,
            TestForecastingHeuristicUtils.TIME,
            TestForecastingHeuristicUtils.TGT
        )
        self.assertEqual(lag, 1, "Wrong lag.")
        self.assertEqual(rw, 2, "Wrong rw.")
        data['grain'] = 'grain'
        lag, rw = analyze_pacf_per_grain(
            data,
            TestForecastingHeuristicUtils.TIME,
            TestForecastingHeuristicUtils.TGT,
            'grain'
        )
        self.assertEqual(lag, 1, "Wrong lag.")
        self.assertEqual(rw, 2, "Wrong rw.")

    def test_analyze_pacf_five_grains(self):
        """Test analysis on more then one grain."""
        data = generate_data_with_lags_and_rw(
            1, 2,
            TestForecastingHeuristicUtils.TIME,
            TestForecastingHeuristicUtils.TGT)
        ngrains = 5
        dfs = []
        for ngrain in range(ngrains):
            df = data.copy()
            df['grain'] = 'grain_{}'.format(ngrain)
            dfs.append(df)
        del data
        grained_data = pd.concat(dfs)
        lag, rw = analyze_pacf_per_grain(
            grained_data,
            TestForecastingHeuristicUtils.TIME,
            TestForecastingHeuristicUtils.TGT,
            'grain'
        )
        self.assertEqual(lag, 1, "Wrong lag.")
        self.assertEqual(rw, 2, "Wrong rw.")
        lag, rw = analyze_pacf_per_grain(
            grained_data,
            TestForecastingHeuristicUtils.TIME,
            TestForecastingHeuristicUtils.TGT,
            ['grain']
        )
        self.assertEqual(lag, 1, "Wrong lag.")
        self.assertEqual(rw, 2, "Wrong rw.")

    def test_analyze_pacf_multi_column_grain(self):
        """Test lag analysis on composite grains."""
        data = generate_data_with_lags_and_rw(
            1, 2,
            TestForecastingHeuristicUtils.TIME,
            TestForecastingHeuristicUtils.TGT)
        ngrains = 4
        dfs = []
        for ngrain in range(ngrains):
            df = data.copy()
            df['grain1'] = 'grain_{}'.format(ngrain % 2)
            df['grain2'] = 'grain_{}'.format(ngrain // 2)
            dfs.append(df)
        del data
        grained_data = pd.concat(dfs)
        lag, rw = analyze_pacf_per_grain(
            grained_data,
            TestForecastingHeuristicUtils.TIME,
            TestForecastingHeuristicUtils.TGT,
            ['grain1', 'grain2']
        )
        self.assertEqual(lag, 1, "Wrong lag.")
        self.assertEqual(rw, 2, "Wrong rw.")

    def test_analyze_pacf_multi_column_grain_invalid(self):
        """Test multi column grain if one grain is invalid."""
        data = generate_data_with_lags_and_rw(
            1, 2,
            TestForecastingHeuristicUtils.TIME,
            TestForecastingHeuristicUtils.TGT)
        ngrains = 4
        dfs = []
        for ngrain in range(ngrains):
            df = data.copy()
            df['grain1'] = 'grain_{}'.format(ngrain % 2)
            df['grain2'] = 'grain_{}'.format(ngrain // 2)
            if ngrain == 2:
                df[TestForecastingHeuristicUtils.TGT] = np.nan
            dfs.append(df)
        del data
        grained_data = pd.concat(dfs)
        with self.assertRaises(DataException):
            lag, rw = analyze_pacf_per_grain(
                grained_data,
                TestForecastingHeuristicUtils.TIME,
                TestForecastingHeuristicUtils.TGT,
                ['grain1', 'grain2'])

    def test_analyze_pacf_one_column_grain_invalid(self):
        """Test multi column grain if one grain is invalid."""
        data = generate_data_with_lags_and_rw(
            1, 2,
            TestForecastingHeuristicUtils.TIME,
            TestForecastingHeuristicUtils.TGT)
        ngrains = 4
        dfs = []
        for ngrain in range(ngrains):
            df = data.copy()
            df['grain'] = 'grain_{}'.format(ngrain)
            if ngrain == 2:
                df[TestForecastingHeuristicUtils.TGT] = np.nan
            dfs.append(df)
        grained_data = pd.concat(dfs)
        del data
        with self.assertRaises(DataException):
            lag, rw = analyze_pacf_per_grain(
                grained_data,
                TestForecastingHeuristicUtils.TIME,
                TestForecastingHeuristicUtils.TGT,
                ['grain'])

    def test_analyze_pacf_no_grain_invalid(self):
        """Test multi column grain if one grain is invalid."""
        data = generate_data_with_lags_and_rw(
            1, 2,
            TestForecastingHeuristicUtils.TIME,
            TestForecastingHeuristicUtils.TGT)
        data[TestForecastingHeuristicUtils.TGT] = np.nan
        with self.assertRaises(DataException):
            lag, rw = analyze_pacf_per_grain(
                data,
                TestForecastingHeuristicUtils.TIME,
                TestForecastingHeuristicUtils.TGT)

    def test_analyze_over_the_limit_grains(self):
        """Test lag analysis if the number of grains is more then limit"""
        data = generate_data_with_lags_and_rw(
            1, 2,
            TestForecastingHeuristicUtils.TIME,
            TestForecastingHeuristicUtils.TGT
        )
        ngrains = 5
        dfs = []
        for ngrain in range(ngrains):
            df = data.copy()
            df['grain'] = 'grain_{}'.format(ngrain)
            dfs.append(df)
        del data
        grained_data = pd.concat(dfs)
        lag, rw = analyze_pacf_per_grain(
            grained_data,
            TestForecastingHeuristicUtils.TIME,
            TestForecastingHeuristicUtils.TGT,
            'grain',
            3
        )
        self.assertEqual(lag, 1, "Wrong lag.")
        self.assertEqual(rw, 2, "Wrong rw.")

    def test_irregular_data_does_not_throw(self):
        """Test if irregular data frame does not break us by itself."""
        def do_test(grains=1, two_grain_columns=False):
            np.random.seed(55)
            LEN = 24
            TWO_GRAINS = ['grain1', 'grain2']
            GRAIN = 'grain'
            y = np.random.rand(LEN)
            y[10:14] = np.nan  # add some NaNs.
            X = pd.DataFrame({
                TestForecastingHeuristicUtils.TIME: pd.date_range('2001-01-01', freq='D', periods=LEN),
                TestForecastingHeuristicUtils.TGT: y,
                'someval': 78
            })
            # Introduce some irregularity.
            X.drop([2, 4, 20, 22], axis=0, inplace=True)
            if grains > 0:
                dfs = []
                for grain in range(grains):
                    df = X.copy()
                    if two_grain_columns:
                        df[TWO_GRAINS[0]] = "g_{}".format(grain // 2)
                        df[TWO_GRAINS[1]] = "g_{}".format(grain % 2)
                    else:
                        df[GRAIN] = "g_{}".format(grain)
                    dfs.append(df)
                X = pd.concat(dfs)

            if grains == 0:
                grain = None
            elif two_grain_columns:
                grain = TWO_GRAINS
            else:
                grain = GRAIN
            # Implicitly check that we are not failing.
            analyze_pacf_per_grain(
                X,
                TestForecastingHeuristicUtils.TIME,
                TestForecastingHeuristicUtils.TGT,
                grain
            )

        do_test(0)
        do_test(1)
        do_test(3)
        do_test(1, True)
        do_test(4, True)

    def test_linalg_error(self):
        """Test the behavior of the analysis if the data are the same."""
        data = generate_data_with_lags_and_rw(
            1, 2,
            TestForecastingHeuristicUtils.TIME,
            TestForecastingHeuristicUtils.TGT
        )
        data[TestForecastingHeuristicUtils.TGT] = 55
        data.set_index(TestForecastingHeuristicUtils.TIME, drop=True, inplace=True)
        p, k = analyze_pacf_one_grain(data[TestForecastingHeuristicUtils.TGT])
        self.assertIsNone(p, 'p must be none.')
        self.assertIsNone(k, 'k must be none.')

    def test_linalg_error_only_grain(self):
        """Test if error is raised if the only grain contain the same values."""
        data = generate_data_with_lags_and_rw(
            1, 2,
            TestForecastingHeuristicUtils.TIME,
            TestForecastingHeuristicUtils.TGT
        )
        data[TestForecastingHeuristicUtils.TGT] = 55
        with self.assertRaises(DataException):
            analyze_pacf_per_grain(
                data,
                TestForecastingHeuristicUtils.TIME,
                TestForecastingHeuristicUtils.TGT)

    def test_data_exception_two_grain(self):
        """Test if data exception is raised on both bad grains data."""
        data = generate_data_with_lags_and_rw(
            1, 2,
            TestForecastingHeuristicUtils.TIME,
            TestForecastingHeuristicUtils.TGT
        )
        data[TestForecastingHeuristicUtils.TGT] = 55
        data['grain'] = 'g1'
        data1 = data.copy()
        data1['grain'] = 'g2'
        data = pd.concat([data, data1])
        del data1
        with self.assertRaises(DataException):
            analyze_pacf_per_grain(
                data,
                TestForecastingHeuristicUtils.TIME,
                TestForecastingHeuristicUtils.TGT,
                'grain')

    def test_linalg_error_on_two_grains(self):
        """Test that error should not be raised if data frame contains at least one good grain."""
        data1 = generate_data_with_lags_and_rw(
            1, 2,
            TestForecastingHeuristicUtils.TIME,
            TestForecastingHeuristicUtils.TGT
        )
        data1[TestForecastingHeuristicUtils.TGT] = 55
        data1['grain'] = 'g1'
        data2 = generate_data_with_lags_and_rw(
            1, 2,
            TestForecastingHeuristicUtils.TIME,
            TestForecastingHeuristicUtils.TGT
        )
        data2['grain'] = 'g2'
        X = pd.concat([data1, data2])
        lags, rw = analyze_pacf_per_grain(
            X,
            TestForecastingHeuristicUtils.TIME,
            TestForecastingHeuristicUtils.TGT,
            'grain')
        self.assertTrue(isinstance(lags, int), "Lags has a wrong type.")
        self.assertTrue(isinstance(rw, int), "Window size has a wrong type.")
        self.assertEqual(lags, 1, 'Wrong lags.')
        self.assertEqual(rw, 2, 'Wrong rolling window.')

    def test_get_frequency_safe_regular(self):
        """Test if frequency may be inferred from the data frame."""
        self._do_test_frequency_infetence(False)

    def test_get_frequency_safe_irregular(self):
        """Test if irregular frequency also will work."""
        self._do_test_frequency_infetence(True)

    def _do_test_frequency_infetence(self, drop_data=False):
        for freq in TestForecastingHeuristicUtils.SUPPORTED_OFFSETS:
            dates = pd.DataFrame({
                'date': pd.date_range('2019-05-07', periods=42, freq=freq),
                'val': 42
            })
            if(drop_data):
                if not (hasattr(to_offset(freq), "delta") or hasattr(to_offset(freq), "_inc")):
                    continue
                dates.drop([2, 4, 6, 7, 9, 11], axis=0, inplace=True)
            dates.set_index('date', drop=True, inplace=True)
            returned_freq = get_frequency_safe(dates.index)
            # We cannot compare offsets directly, because offset aliases may differ:
            # pandas will detect CustomBusinesDaty as BusinessDay, because
            # by default they have the same calendar.
            # Make sure we have comparable index.
            date_grid = pd.date_range(
                start=dates.index.min(),
                end=dates.index.max(),
                freq=returned_freq)
            self.assertTrue(all(x in date_grid for x in dates.index), 'Wrong frequency inferred for {}.'.format(freq))

    def test_get_heuristic_max_horison(self):
        """Test hgeuristic max_horison."""
        dict_freq_expect = {
            'T': 60,
            'H': 24,
            'M': 12,
            'Q': 4,
            'Y': 1
        }

        def do_test_heuristic_max_horizon(freq, expected_max_horizom):
            """Do the actual test."""
            data = pd.DataFrame({
                TestForecastingHeuristicUtils.TIME: pd.date_range('2019-05-07', periods=42, freq=freq),
                'val': 42
            })
            max_horizon = get_heuristic_max_horison(data, TestForecastingHeuristicUtils.TIME)
            self.assertEqual(
                max_horizon, expected_max_horizom,
                "Wrong max_horizon for frequency {}.".format(freq))

        # Frequencies with heuristics.
        for freq, exp in dict_freq_expect.items():
            do_test_heuristic_max_horizon(freq, exp)

        # One of unsupported frequencies.
        do_test_heuristic_max_horizon('W', 1)


if __name__ == '__main__':
    unittest.main()
