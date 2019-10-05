from pytest import mark, raises
from unittest.mock import patch
from src.utils import table
from tests import helpers


@patch.object(table, "set_logs")
@patch.object(table, "set_title")
def test_generate_table_vis_state(set_title, set_logs):
    table.generate_table_vis_state("bfk", ["bla"])
    assert set_title.call_count == 1
    assert set_logs.call_count == 1


def test_generate_table_vis_state_integration():
    query = [{"query": "One", "label": "One"},
             {"query": "Two", "label": "Two"}]
    assert table.generate_table_vis_state("Valid", query) == \
        helpers.get_test_results_json_file(
            "valid_table_vis_state_results.json")


def test_set_title_value_error():
    with raises(ValueError):
        table.set_title(None)


@mark.parametrize(
    "path_name, expected",
    [
        ("path", "[Generated] - path"),
        ("pfdsafdsa ", "[Generated] - pfdsafdsa "),
        ("", "[Generated] - ")
    ]
)
def test_set_title(path_name, expected):
    table.set_title(path_name)
    assert table.vis_state["title"] == expected


@mark.parametrize(
    "logs, expected",
    [
        (None, "empty_table_vis_state_results.json"),
        ([],
         "empty_table_vis_state_results.json"),
        ([{"query": "one", "label": "one"}],
         "one_table_vis_state_results.json"),
        ([{"query": "One", "label": "One"}, {"query": "Two", "label": "Two"}],
         "two_table_vis_state_results.json")
    ],
)
def test_set_logs(logs, expected):
    table.set_logs(logs)
    assert helpers.get_test_results_json_file(expected) == table.vis_state
