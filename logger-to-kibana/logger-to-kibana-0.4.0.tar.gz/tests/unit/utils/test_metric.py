from pytest import mark, raises
from unittest.mock import patch
from src.utils import metric
from tests import helpers


@patch.object(metric, "set_logs")
@patch.object(metric, "set_title")
def test_generate_metric_vis_state(set_title, set_logs):
    metric.generate_metric_vis_state("bfk", ["bla"])
    assert set_title.call_count == 1
    assert set_logs.call_count == 1


def test_generate_metric_vis_state_integration():
    query = [{"query": "One", "label": "One"},
             {"query": "Two", "label": "Two"}]
    assert metric.generate_metric_vis_state("Valid", query) == \
        helpers.get_test_results_json_file("valid_metric_vis_state_results.json")


def test_set_title_value_error():
    with raises(ValueError):
        metric.set_title(None)


@mark.parametrize(
    "path_name, expected",
    [
        ("path", "[Generated] - path"),
        ("pfdsafdsa ", "[Generated] - pfdsafdsa "),
        ("", "[Generated] - ")
    ]
)
def test_set_title(path_name, expected):
    metric.set_title(path_name)
    assert metric.vis_state["title"] == expected


@mark.parametrize(
    "logs, expected",
    [
        (None, "empty_metric_vis_state_results.json"),
        ([],
         "empty_metric_vis_state_results.json"),
        ([{"query": "one", "label": "one"}],
         "one_metric_vis_state_results.json"),
        ([{"query": "One", "label": "One"}, {"query": "Two", "label": "Two"}],
         "two_metric_vis_state_results.json")
    ],
)
def test_set_logs(logs, expected):
    metric.set_logs(logs)
    assert helpers.get_test_results_json_file(expected) == metric.vis_state
