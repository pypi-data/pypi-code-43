import json
import os
from io import StringIO

import numpy as np
import pandas as pd

from azureml.studio.common.datatable.data_table import DataTable
from azureml.studio.modules.ml.common.constants import ScoreColumnConstants
from azureml.studio.modulehost.handler.sidecar_files import SideCarFileBundle, Visualizer
from azureml.studio.modules.ml.evaluate.evaluate_generic_module.evaluate_generic_module import EvaluateModelModule


def script_directory():
    return os.path.dirname(os.path.abspath(__file__))


def _base_library():
    return os.path.join(script_directory(), 'input', 'evaluate_binary_model')


def _prepare_data():
    data_path = os.path.join(_base_library(), 'sample_scored_result.csv')
    ref_path = os.path.join(_base_library(), 'bi_model.visualization')
    df = pd.read_csv(data_path)
    dt = DataTable(df)
    dt.meta_data.label_column_name = 'income'
    dt.meta_data.score_column_names = {
        ScoreColumnConstants.BinaryClassScoredLabelType: ScoreColumnConstants.ScoredLabelsColumnName,
        ScoreColumnConstants.CalibratedScoreType: ScoreColumnConstants.ScoredProbabilitiesColumnName
    }
    with open(ref_path) as f:
        ref = json.load(f)
    return dt, ref


def _simple_object_accordance(ref_dict, out_dict, allow_recursion=False):
    for key, value in ref_dict.items():
        assert key in out_dict
        assert isinstance(value, type(out_dict[key]))
        if not isinstance(value, (list, dict)):
            if isinstance(value, str):
                assert value == out_dict[key]
            else:
                assert np.isclose(value, out_dict[key])
        elif allow_recursion:
            _simple_object_accordance(value, ref_dict[key])


def _data_points_accordance(data_points_ref, data_points_out):
    assert len(data_points_ref) <= len(data_points_out)
    data_points_length = len(data_points_ref)
    ref_index = 0
    for data_point_out in data_points_out:
        data_point_ref = data_points_ref[ref_index]
        if not np.isclose(data_point_ref["probability"], data_point_out["probability"]):
            continue
        _simple_object_accordance(data_point_ref, data_point_out, allow_recursion=True)
        ref_index += 1
    assert ref_index == data_points_length


def _chart_accordance(ref_dict, out_dict):
    # chart should have the following items: auc -> float, min -> float, data -> data point list,
    # coarseData -> bucket bin list, positiveLabel -> str, negativeLabel -> str
    _simple_object_accordance(ref_dict, out_dict)
    data_points_key = 'data'
    data_points_ref = ref_dict[data_points_key]
    data_points_out = out_dict[data_points_key]
    _data_points_accordance(data_points_ref, data_points_out)
    binner_key = 'coarseData'
    binner_ref = ref_dict[binner_key]
    binner_out = ref_dict[binner_key]
    [_simple_object_accordance(x, y, allow_recursion=True) for x, y in zip(binner_ref, binner_out)]


def _report_data_accordance(ref_dict, out_dict):
    # report_data should have the following items: chart -> dict, reportName -> str
    _simple_object_accordance(ref_dict, out_dict)
    chart_key = 'chart'
    _chart_accordance(ref_dict[chart_key], out_dict[chart_key])


def _visualization_result_accordance(ref_dict, out_dict):
    # visualization_result should have the following items: visualizationType -> str, reports -> report list
    _simple_object_accordance(ref_dict, out_dict)
    report_key = 'reports'
    assert len(out_dict[report_key]) == len(ref_dict[report_key])
    for report_ref, report_out in zip(ref_dict[report_key], out_dict[report_key]):
        _report_data_accordance(report_ref, report_out)


def test_report_result():
    dt, ref_dict = _prepare_data()
    res = EvaluateModelModule.run(scored_data=dt, scored_data_to_compare=None)[0]
    assert isinstance(res, SideCarFileBundle)

    visualizer = res.visualizer
    assert isinstance(visualizer, Visualizer)

    visualization_stream = StringIO()
    visualizer.dump(visualization_stream)

    visualization_json = visualization_stream.getvalue()
    report_data_dict = json.loads(visualization_json)
    _visualization_result_accordance(ref_dict, report_data_dict)
