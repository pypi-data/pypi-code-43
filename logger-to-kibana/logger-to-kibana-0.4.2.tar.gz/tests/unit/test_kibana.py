import pytest
import src.kibana as kib
from unittest.mock import patch
from tests import helpers


@patch.object(kib, "group_items")
@patch.object(kib, "get_title_from_group")
@patch.object(kib, "generate_folder_visualization")
@patch.object(kib, "send_visualization")
@pytest.mark.parametrize(
    "items_group, expected_calls",
    [
        (None, 0),
        ([], 0),
        ([[{'subfolder': 'bla', 'filename': 'file', 'function': None}]], 1)
    ]
)
def test_generate_and_send_visualizations(
        send, generate, get_title, group_items,
        items_group, expected_calls):
    group_items.return_value = items_group
    kib.generate_and_send_visualizations("test", [])
    assert group_items.call_count == 1
    assert get_title.call_count == expected_calls
    assert generate.call_count == expected_calls
    assert send.call_count == expected_calls


@patch.object(kib, "group_items")
@patch.object(kib, "get_title_from_group")
@patch.object(kib, "generate_folder_visualization")
@pytest.mark.parametrize(
    "items_group, expected_calls",
    [
        (None, 0),
        ([], 0),
        ([[{'subfolder': 'bla', 'filename': 'file', 'function': None}]], 1)
    ]
)
def test_generate_folder_visualizations(
        generate, get_title, group_items,
        items_group, expected_calls):
    group_items.return_value = items_group
    kib.generate_folder_visualizations("test", [])
    assert group_items.call_count == 1
    assert get_title.call_count == expected_calls
    assert generate.call_count == expected_calls



@pytest.mark.parametrize(
    "folder_name, group, expected",
    [
        ("bla",
         {'subfolder': 'ble', 'filename': 'bli', 'function': 'blo'},
         "bla ble bli blo"),
        ("folder",
         {'subfolder': 'sub', 'filename': 'file', 'function': 'func'},
         "folder sub file func"),
    ]
)
def test_get_title_from_group(folder_name, group, expected):
    assert kib.get_title_from_group(folder_name, group) == expected



@pytest.mark.parametrize(
    "items, expected",
    [
        ([{'subfolder': 'ble', 'filename': 'bli', 'function': 'blo'}],
         [[{'subfolder': 'ble', 'filename': 'bli', 'function': 'blo'}]]
         ),
        ([{'subfolder': 'ble', 'filename': 'bla', 'function': 'blo'},
         {'subfolder': 'ble', 'filename': 'bli', 'function': 'blo'},
         {'subfolder': 'ble', 'filename': 'bli', 'function': 'blo'},
         {'subfolder': 'bli', 'filename': 'bli', 'function': 'blo'},
         {'subfolder': 'bli', 'filename': 'blo', 'function': 'blo'}],
         [[{'subfolder': 'ble', 'filename': 'bla', 'function': 'blo'}],
          [{'subfolder': 'ble', 'filename': 'bli', 'function': 'blo'},
           {'subfolder': 'ble', 'filename': 'bli', 'function': 'blo'}],
          [{'subfolder': 'bli', 'filename': 'bli', 'function': 'blo'}],
          [{'subfolder': 'bli', 'filename': 'blo', 'function': 'blo'}]],
         )
    ]
)
def test_group_items(items, expected):
    assert expected == kib.group_items(items)


@pytest.mark.parametrize(
    "path_name, items, expected",
    [
        ("/", [], "visualization_with_empty_vis_state.json"),
        ("Valid", [], "visualization_with_valid_values.json")
    ]
)
def test_generate_folder_visualization_integration(path_name, items, expected):
    kib.config.kibana.VisualizationType = 'table'
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
