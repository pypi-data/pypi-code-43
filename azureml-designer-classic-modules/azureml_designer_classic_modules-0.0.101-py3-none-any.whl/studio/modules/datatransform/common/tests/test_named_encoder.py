import pandas as pd

import numpy as np
import pytest

from azureml.studio.modules.datatransform.common.named_encoder import NamedLogNormalEncoder, NamedZScoreEncoder, \
    NamedMinMaxEncoder


def test_use_zero_lognormal_meet_constant_column():
    series = pd.Series([2, 2, 2])
    ne = NamedLogNormalEncoder('test_column', constant_column_option=True)
    ne.fit(series)
    np.testing.assert_array_almost_equal(ne.transform(series), [0., 0., 0.])
    np.testing.assert_equal(ne.transform(pd.Series(np.array([1, 2, 3]))), [0., 0., 0.])
    np.testing.assert_equal(ne.transform(pd.Series(np.array([1, 2, 3, np.nan]))), [0., 0., 0., np.nan])


def test_use_zero_lognomal_meet_constant_column_with_nan():
    series = pd.Series([1, 1, np.nan, 1, np.nan])
    ne = NamedLogNormalEncoder('test_column', constant_column_option=True)
    ne.fit(series)
    np.testing.assert_array_almost_equal(ne.transform(series), [0., 0., np.nan, 0., np.nan])


def test_not_use_zero_lognormal_meet_constant_column():
    series = pd.Series([2, 2, 2])
    ne = NamedLogNormalEncoder('test_column', constant_column_option=False)
    ne.fit(series)
    np.testing.assert_array_almost_equal(ne.transform(series), [np.nan, np.nan, np.nan])
    np.testing.assert_equal(ne.transform(pd.Series(np.array([1, 2, 3]))), [np.nan, np.nan, np.nan])
    np.testing.assert_equal(ne.transform(pd.Series(np.array([1, 2, 3, np.nan]))), [np.nan, np.nan, np.nan, np.nan])


def test_use_zero_min_max_meet_constant_column():
    series = pd.Series([2, 2, 2])
    ne = NamedMinMaxEncoder('test_column', constant_column_option=True)
    ne.fit(series)
    np.testing.assert_array_almost_equal(ne.transform(series), [0., 0., 0.])
    np.testing.assert_equal(ne.transform(pd.Series(np.array([1, 2, 3]))), [0., 0., 0.])
    np.testing.assert_equal(ne.transform(pd.Series(np.array([1, 2, 3, np.nan]))), [0., 0., 0., np.nan])


def test_use_zero_min_max_meet_constant_column_with_nan():
    series = pd.Series([1, 1, np.nan, 1, np.nan])
    ne = NamedMinMaxEncoder('test_column', constant_column_option=True)
    ne.fit(series)
    np.testing.assert_array_almost_equal(ne.transform(series), [0., 0., np.nan, 0., np.nan])


def test_not_use_zero_min_max_meet_constant_column():
    series = pd.Series([2, 2, 2])
    ne = NamedMinMaxEncoder('test_column', constant_column_option=False)
    ne.fit(series)
    np.testing.assert_array_almost_equal(ne.transform(series), [np.nan, np.nan, np.nan])
    np.testing.assert_equal(ne.transform(pd.Series(np.array([1, 2, 3]))), [np.nan, np.nan, np.nan])
    np.testing.assert_equal(ne.transform(pd.Series(np.array([1, 2, 3, np.nan]))), [np.nan, np.nan, np.nan, np.nan])


def test_use_zero_zscore_meet_constant_column():
    series = pd.Series([2, 2, 2])
    ne = NamedZScoreEncoder('test_column', constant_column_option=True)
    ne.fit(series)
    np.testing.assert_array_almost_equal(ne.transform(series), [0., 0., 0.])
    np.testing.assert_equal(ne.transform(pd.Series(np.array([1, 2, 3]))), [0., 0., 0.])
    np.testing.assert_equal(ne.transform(pd.Series(np.array([1, 2, 3, np.nan]))), [0., 0., 0., np.nan])


def test_use_zero_zscore_meet_constant_column_with_nan():
    series = pd.Series([1, 1, np.nan, 1, np.nan])
    ne = NamedZScoreEncoder('test_column', constant_column_option=True)
    ne.fit(series)
    np.testing.assert_array_almost_equal(ne.transform(series), [0., 0., np.nan, 0., np.nan])


def test_not_use_zero_zscore_meet_constant_column():
    series = pd.Series([2, 2, 2])
    ne = NamedZScoreEncoder('test_column', constant_column_option=False)
    ne.fit(series)
    np.testing.assert_array_almost_equal(ne.transform(series), [np.nan, np.nan, np.nan])
    np.testing.assert_equal(ne.transform(pd.Series(np.array([1, 2, 3]))), [np.nan, np.nan, np.nan])
    np.testing.assert_equal(ne.transform(pd.Series(np.array([1, 2, 3, np.nan]))), [np.nan, np.nan, np.nan, np.nan])


def _get_src_series_constant_column_with_inf_small_std():
    return pd.Series([1, 1, np.nan, 1, np.nan, np.inf, -np.inf])


def _get_src_series_constant_column_with_inf_big_std():
    return pd.Series([1, 2, np.nan, 4, np.nan, np.inf, -np.inf])


def _get_tgt_transform_use_zero_meet_constant_column_with_inf_small_std():
    return [0., 0., np.nan, 0., np.nan, np.nan, np.nan]


def _get_tgt_transform_not_use_zero_meet_constant_column_with_inf_small_std():
    return [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]


def _get_tgt_transform_lognormal_constant_column_with_inf_big_std():
    return [0.110336, 0.5, np.nan, 0.889664, np.nan, 1., 0.]


def _get_tgt_transform_min_max_constant_column_with_inf_big_std():
    return [0., 0.333333, np.nan, 1., np.nan, np.nan, np.nan]


def _get_tgt_transform_zscore_constant_column_with_inf_big_std():
    return [-1.06904497, -0.26726124, np.nan, 1.33630621, np.nan, np.nan, np.nan]


@pytest.mark.parametrize(
    'src_series, named_encoder, constant_column_option, tgt_transform',
    [
        (_get_src_series_constant_column_with_inf_small_std(), NamedLogNormalEncoder, True,
         _get_tgt_transform_use_zero_meet_constant_column_with_inf_small_std()),
        (_get_src_series_constant_column_with_inf_small_std(), NamedLogNormalEncoder, False,
         _get_tgt_transform_not_use_zero_meet_constant_column_with_inf_small_std()),
        (_get_src_series_constant_column_with_inf_small_std(), NamedMinMaxEncoder, True,
         _get_tgt_transform_use_zero_meet_constant_column_with_inf_small_std()),
        (_get_src_series_constant_column_with_inf_small_std(), NamedMinMaxEncoder, False,
         _get_tgt_transform_not_use_zero_meet_constant_column_with_inf_small_std()),
        (_get_src_series_constant_column_with_inf_small_std(), NamedZScoreEncoder, True,
         _get_tgt_transform_use_zero_meet_constant_column_with_inf_small_std()),
        (_get_src_series_constant_column_with_inf_small_std(), NamedZScoreEncoder, False,
         _get_tgt_transform_not_use_zero_meet_constant_column_with_inf_small_std()),
        (_get_src_series_constant_column_with_inf_big_std(), NamedLogNormalEncoder, True,
         _get_tgt_transform_lognormal_constant_column_with_inf_big_std()),
        (_get_src_series_constant_column_with_inf_big_std(), NamedLogNormalEncoder, False,
         _get_tgt_transform_lognormal_constant_column_with_inf_big_std()),
        (_get_src_series_constant_column_with_inf_big_std(), NamedMinMaxEncoder, True,
         _get_tgt_transform_min_max_constant_column_with_inf_big_std()),
        (_get_src_series_constant_column_with_inf_big_std(), NamedMinMaxEncoder, False,
         _get_tgt_transform_min_max_constant_column_with_inf_big_std()),
        (_get_src_series_constant_column_with_inf_big_std(), NamedZScoreEncoder, True,
         _get_tgt_transform_zscore_constant_column_with_inf_big_std()),
        (_get_src_series_constant_column_with_inf_big_std(), NamedZScoreEncoder, False,
         _get_tgt_transform_zscore_constant_column_with_inf_big_std()),
    ]
)
def test_constant_column_with_inf(src_series, named_encoder, constant_column_option, tgt_transform):
    ne = named_encoder('test_column', constant_column_option=constant_column_option)
    ne.fit(src_series)
    np.testing.assert_array_almost_equal(ne.transform(src_series), tgt_transform)
