import json
from src.utils import visualization
from pytest import mark, raises
from unittest.mock import patch
from tests import helpers


@mark.parametrize(
    "path_name, vis_state, expected",
    [
        ("Valid", [],
         "visualization_with_valid_values.json"),
        ("/", [],
         "visualization_with_empty_vis_state.json")
    ]
)
def test_generate_visualization_integration(path_name, vis_state, expected):
    visualization.config.kibana.VisualizationType = 'table'
    assert helpers.get_test_results_json_file(expected) == \
        visualization.generate_visualization(path_name, vis_state)


@patch.object(visualization, "generate_vis_state")
@patch.object(visualization, "set_vis_state")
@patch.object(visualization, "set_title")
def test_generate_visualization(set_title, set_vis_state, generate_vis_state):
    visualization.generate_visualization("path", {"vis_state"})
    assert set_title.call_count == 1
    assert generate_vis_state.call_count == 1
    assert set_vis_state.call_count == 1


@patch.object(visualization.metric, "generate_metric_vis_state")
@patch.object(visualization.table, "generate_table_vis_state")
@mark.parametrize(
    "visType, metric_calls, table_calls",
    [
        (None, 0, 1),
        ("table", 0, 1),
        ("metric", 1, 0),
    ]
)
def test_generate_vis_state(
        table, metric,
        visType, metric_calls, table_calls):
    visualization.config.kibana.VisualizationType = visType
    visualization.generate_vis_state("title", [])
    assert table.call_count == table_calls
    assert metric.call_count == metric_calls


def test_set_title_value_error():
    with raises(ValueError):
        visualization.set_title(None)


@mark.parametrize(
    "path_name, expected",
    [
        ("Secret", "[Generated] - Secret"),
        ("fdsafd", "[Generated] - fdsafd")
    ]
)
def test_set_title(path_name, expected):
    visualization.set_title(path_name)
    assert visualization.visualization['title'] == expected


def test_set_vis_state_value_error():
    with raises(ValueError):
        visualization.set_vis_state(None)


@mark.parametrize(
    "vis_state, expected",
    [
        ({}, "{}"),
        ({"some": "stuff"}, "{\"some\": \"stuff\"}")
    ]
)
def test_set_vis_state(vis_state, expected):
    visualization.set_vis_state(vis_state)
    assert visualization.visualization['visState'] == expected
