import pytest
import src.kibana as kib
from unittest.mock import patch
from tests import helpers


@patch.object(kib, "generate_folder_visualization")
@patch.object(kib, "send_visualization")
def test_generate_and_send_visualization(generate, send):
    kib.generate_and_send_visualization("test", [])
    assert generate.call_count == 1
    assert send.call_count == 1


@pytest.mark.parametrize(
    "path_name, items, expected",
    [
        ("/", [], "visualization_with_empty_vis_state.json"),
        ("Valid", [], "visualization_with_valid_values.json")
    ]
)
def test_generate_folder_visualization_integration(path_name, items, expected):
    assert helpers.get_test_results_json_file(expected) == \
        kib.generate_folder_visualization(path_name, items)


@patch.object(kib.visualization, "generate_visualization")
def test_generate_folder_visualization(visualization):
    kib.generate_folder_visualization("test", [])
    assert visualization.call_count == 1


@patch.object(kib, "requests")
@pytest.mark.parametrize(
    "path_name, items, expected",
    [
        ("path_name", [], {})
    ]
)
def test_send_visualization(requests, path_name, items, expected):
    expected == kib.send_visualization(path_name, items)
