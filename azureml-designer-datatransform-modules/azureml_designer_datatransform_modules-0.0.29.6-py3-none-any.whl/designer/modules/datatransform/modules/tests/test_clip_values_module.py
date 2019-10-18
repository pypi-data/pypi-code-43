import os
import tempfile
import pytest
import pandas as pd
from azureml.designer.modules.datatransform.modules.clip_values_module import ClipValuesModule, Threshold, ClipMode, ReplaceMode
from azureml.designer.modules.datatransform.tools.dataframe_utils import compare_dataframe
from azureml.studio.core.utils.column_selection import ColumnSelectionBuilder
from azureml.studio.core.io.data_frame_directory import save_data_frame_to_directory, load_data_frame_from_directory
from azureml.studio.core.data_frame_schema import DataFrameSchema
from azureml.designer.modules.datatransform.tools.column_selection_utils import convert_column_selection_to_json

@pytest.fixture
def dataframe1():
    return pd.DataFrame(data=[
        [0, 2, 1],
        [0, 8, 3],
        [0, 2, 1],
        [1, 5, 9],
        [1, 2, 1],
        [1, 8, 9]
    ], columns=["Col 0", "Col 1", "Col 2"])


@pytest.fixture
def expected_dataframe_clip_hi_rep_median(include_indicator_columns):
    return pd.DataFrame(
        data=[[0, 0.0, False, 2, 2, False, 1, 1.0, False],
              [0, 0, False, 8, 3.5, True,  3, 3, False],
              [0, 0, False, 2, 2, False, 1, 1, False],
              [1, 1, False, 5, 5, False, 9, 2, True],
              [1, 1, False, 2, 2, False, 1, 1, False],
              [1, 1, False, 8, 3.5, True,  9, 2, True]],
        columns=include_indicator_columns)

@pytest.fixture
def expected_dataframe_clip_hi_rep_median_inplace_indicator(inplace_include_indicator_columns):
    return pd.DataFrame(
        data=[[0.0, False, 2, False, 1.0, False],
              [0, False, 3.5, True, 3, False],
              [0, False, 2, False, 1, False],
              [1, False, 5, False, 2, True],
              [1, False, 2, False, 1, False],
              [1, False, 3.5, True, 2, True]],
        columns=inplace_include_indicator_columns)

@pytest.fixture
def expected_dataframe_clip_hi_rep_mean(include_indicator_columns):
    return pd.DataFrame(
        data=[[0, 0.0, False, 2, 2.0, False, 1, 1.0, False],
              [0, 0, False, 8, 4.5, True,  3, 3, False],
              [0, 0, False, 2, 2, False, 1, 1, False],
              [1, 1, False, 5, 5, False, 9, 4, True],
              [1, 1, False, 2, 2, False, 1, 1, False],
              [1, 1, False, 8, 4.5, True,  9, 4, True]],
        columns=include_indicator_columns)


@pytest.fixture
def expected_dataframe_clip_low_rep_median(include_indicator_columns):
    return pd.DataFrame(
        data=[[0, 0.5, True, 2, 3.5, True, 1, 2.0, True],
              [0, 0.5, True, 8, 8.0, False,  3, 3, False],
              [0, 0.5, True, 2, 3.5, True, 1, 2, True],
              [1, 0.5, True, 5, 5, False, 9, 9, False],
              [1, 0.5, True, 2, 3.5, True, 1, 2, True],
              [1, 0.5, True, 8, 8, False,  9, 9, False]],
        columns=include_indicator_columns)


@pytest.fixture
def expected_dataframe_clip_low_rep_mean(include_indicator_columns):
    return pd.DataFrame(
        data=[[0, 0.5, True, 2, 4.5, True, 1, 4.0, True],
              [0, 0.5, True, 8, 8.0, False,  3, 3, False],
              [0, 0.5, True, 2, 4.5, True, 1, 4, True],
              [1, 0.5, True, 5, 5, False, 9, 9, False],
              [1, 0.5, True, 2, 4.5, True, 1, 4, True],
              [1, 0.5, True, 8, 8, False,  9, 9, False]],
        columns=include_indicator_columns)


@pytest.fixture
def include_indicator_columns():
    return ["Col 0", "Col 0_clipped_value", "Col 0_clipped",
            "Col 1", "Col 1_clipped_value", "Col 1_clipped",
            "Col 2", "Col 2_clipped_value", "Col 2_clipped"]

@pytest.fixture
def exclude_indicator_columns():
    return ["Col 0", "Col 0_clipped_value",
            "Col 1", "Col 1_clipped_value",
            "Col 2", "Col 2_clipped_value"]

@pytest.fixture
def inplace_include_indicator_columns():
    return ["Col 0", "Col 0_clipped",
            "Col 1", "Col 1_clipped",
            "Col 2", "Col 2_clipped"]

@pytest.fixture
def column_selection():
    return convert_column_selection_to_json(ColumnSelectionBuilder().include_all().exclude_col_names("Col 1"))


def test_clip_hi_rep_median_incl_indicators(dataframe1, expected_dataframe_clip_hi_rep_median):
    assert clip_values_module_test_kernal(input_data=dataframe1, clipmode=ClipMode.ClipPeaks, threshold=Threshold.Constant,
                                          up_constant_threshold=6.0, up_replace_mode=ReplaceMode.Median,
                                          expect_table=expected_dataframe_clip_hi_rep_median)


def test_clip_hi_rep_median_incl_indicators_inplace(dataframe1, expected_dataframe_clip_hi_rep_median_inplace_indicator):
    assert clip_values_module_test_kernal(input_data=dataframe1, clipmode=ClipMode.ClipPeaks, threshold=Threshold.Constant,
                                          up_constant_threshold=6.0, up_replace_mode=ReplaceMode.Median,
                                          expect_table=expected_dataframe_clip_hi_rep_median_inplace_indicator,inplace_flag=True)

def test_clip_hi_rep_median_incl_indicators_column_selection(dataframe1, expected_dataframe_clip_hi_rep_median, column_selection):
    assert clip_values_module_test_kernal(input_data=dataframe1, clipmode=ClipMode.ClipPeaks, threshold=Threshold.Constant,
                                          up_constant_threshold=6.0, up_replace_mode=ReplaceMode.Median,
                                          expect_table=expected_dataframe_clip_hi_rep_median.drop(columns=["Col 1_clipped_value", "Col 1_clipped"]), column_selector=column_selection)


def test_clip_hi_rep_median_excl_indicators(dataframe1, expected_dataframe_clip_hi_rep_median, exclude_indicator_columns):
    assert clip_values_module_test_kernal(input_data=dataframe1, clipmode=ClipMode.ClipPeaks, threshold=Threshold.Constant,
                                          up_constant_threshold=6.0, up_replace_mode=ReplaceMode.Median,
                                          expect_table=expected_dataframe_clip_hi_rep_median[exclude_indicator_columns], indicator_flag=False)


def test_clip_hi_rep_mean_incl_indicators(dataframe1, expected_dataframe_clip_hi_rep_mean):
    assert clip_values_module_test_kernal(input_data=dataframe1, clipmode=ClipMode.ClipPeaks, threshold=Threshold.Constant,
                                          up_constant_threshold=6.0, up_replace_mode=ReplaceMode.Mean,
                                          expect_table=expected_dataframe_clip_hi_rep_mean)


def test_clip_hi_rep_mean_excl_indicators(dataframe1, expected_dataframe_clip_hi_rep_mean, exclude_indicator_columns):
    assert clip_values_module_test_kernal(input_data=dataframe1, clipmode=ClipMode.ClipPeaks, threshold=Threshold.Constant,
                                          up_constant_threshold=6.0, up_replace_mode=ReplaceMode.Mean,
                                          expect_table=expected_dataframe_clip_hi_rep_mean[exclude_indicator_columns], indicator_flag=False)


def test_clip_low_rep_median_incl_indicators(dataframe1, expected_dataframe_clip_low_rep_median):
    assert clip_values_module_test_kernal(input_data=dataframe1, clipmode=ClipMode.ClipSubPeaks, threshold=Threshold.Constant,
                                          bottom_constant_threshold=3.0, bottom_replace_mode=ReplaceMode.Median,
                                          expect_table=expected_dataframe_clip_low_rep_median)


def test_clip_low_rep_median_excl_indicators(dataframe1, expected_dataframe_clip_low_rep_median, exclude_indicator_columns):
    assert clip_values_module_test_kernal(input_data=dataframe1, clipmode=ClipMode.ClipSubPeaks, threshold=Threshold.Constant,
                                          bottom_constant_threshold=3.0, bottom_replace_mode=ReplaceMode.Median,
                                          expect_table=expected_dataframe_clip_low_rep_median[exclude_indicator_columns], indicator_flag=False)


def test_clip_low_rep_mean_incl_indicators(dataframe1, expected_dataframe_clip_low_rep_mean):
    assert clip_values_module_test_kernal(input_data=dataframe1, clipmode=ClipMode.ClipSubPeaks, threshold=Threshold.Constant,
                                          bottom_constant_threshold=3.0, bottom_replace_mode=ReplaceMode.Mean,
                                          expect_table=expected_dataframe_clip_low_rep_mean)


def test_clip_low_rep_mean_excl_indicators(dataframe1, expected_dataframe_clip_low_rep_mean, exclude_indicator_columns):
    assert clip_values_module_test_kernal(input_data=dataframe1, clipmode=ClipMode.ClipSubPeaks, threshold=Threshold.Constant,
                                          bottom_constant_threshold=3.0, bottom_replace_mode=ReplaceMode.Mean,
                                          expect_table=expected_dataframe_clip_low_rep_mean[exclude_indicator_columns], indicator_flag=False)


# no parameter dependency checking at this moment
# def test_raise_error(dataframe1):
#     with pytest.raises(ValueError):
#         clip_values_module_test_kernal(input_data=dataframe1, clipmode=ClipMode.ClipPeaks, threshold=Threshold.Constant,
#                                           bottom_constant_threshold=3.0, bottom_replace_mode=ReplaceMode.Mean,
#                                           expect_table=None, indicator_flag=False)

def clip_values_module_test_kernal(
        input_data: pd.DataFrame,
        clipmode: ClipMode,
        threshold: Threshold,
        expect_table: pd.DataFrame,
        up_replace_mode: ReplaceMode = None,
        bottom_replace_mode: ReplaceMode = None,
        up_percentile_threshold: int = None,
        bottom_percentile_threshold: int = None,
        up_constant_threshold: float = None,
        bottom_constant_threshold: float = None,
        inplace_flag: bool = False,
        indicator_flag: bool = True,
        column_selector: str = None
) -> bool:
    with tempfile.TemporaryDirectory(dir='./') as tmpdirname:
        input_path = os.path.join(tmpdirname, 'input//')
        # os.makedirs(os.path.dirname(input_path))
        # input_data.to_parquet(input_path)
        schema = DataFrameSchema.data_frame_to_dict(input_data)
        save_data_frame_to_directory(input_path, data=input_data, schema=schema)
        output_path = os.path.join(tmpdirname, 'output//')
        module = ClipValuesModule()
        module.insert_arguments(**({
            'clipmode': clipmode,
            'threshold': threshold,
            'up_replace_mode': up_replace_mode,
            'bottom_replace_mode': bottom_replace_mode,
            'up_percentile_threshold': up_percentile_threshold,
            'bottom_percentile_threshold': bottom_percentile_threshold,
            'up_constant_threshold': up_constant_threshold,
            'bottom_constant_threshold': bottom_constant_threshold,
            'inplace_flag': inplace_flag,
            'indicator_flag': indicator_flag,
            'column_selector': column_selector if column_selector else convert_column_selection_to_json(ColumnSelectionBuilder().include_all()),
            'input': os.path.dirname(input_path),
            'dataset': os.path.dirname(output_path)}))
        module.train()
        result = load_data_frame_from_directory(output_path).data
        # result = pd.read_parquet(output_path)
        if expect_table is None:
            return True
        return compare_dataframe(result, expect_table)
