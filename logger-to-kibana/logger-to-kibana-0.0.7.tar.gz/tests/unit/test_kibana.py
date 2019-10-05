import pytest
import src.kibana as kib
from unittest.mock import patch
from tests import helpers


@patch.object(kib, "generate_folder_visualisation")
@patch.object(kib, "send_visualisation")
def test_generate_and_send_visualisation(generate, send):
    kib.generate_and_send_visualisation("test", [])
    assert generate.call_count == 1
    assert send.call_count == 1


@pytest.mark.parametrize(
    "path_name, items, expected",
    [
        ("/", [], "visualisation_with_empty_vis_state.json"),
        ("Valid", [], "visualisation_with_valid_values.json")
    ]
)
def test_generate_folder_visualisation_integration(path_name, items, expected):
    assert helpers.get_test_results_json_file(expected) == \
        kib.generate_folder_visualisation(path_name, items)


@patch.object(kib.table, "generate_table_vis_state")
@patch.object(kib.visualisation, "generate_visualisation")
def test_generate_folder_visualisation(table, visualisation):
    kib.generate_folder_visualisation("test", [])
    assert table.call_count == 1
    assert visualisation.call_count == 1


@patch.object(kib, "requests")
@pytest.mark.parametrize(
    "path_name, items, expected",
    [
        ("path_name", [], {})
    ]
)
def test_send_visualisation(requests, path_name, items, expected):
    expected == kib.send_visualisation(path_name, items)
