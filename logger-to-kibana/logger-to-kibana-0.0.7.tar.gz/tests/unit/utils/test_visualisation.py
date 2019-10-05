import json
from src.utils import visualisation
from pytest import mark, raises
from unittest.mock import patch
from tests import helpers


@mark.parametrize(
    "path_name, vis_state, expected",
    [
        ("Valid", "{\"title\": \"[Generated] - Valid\", \"type\": \"table\", \
         \"params\": {\"perPage\": 20, \"showPartialRows\": false, \
         \"showMetricsAtAllLevels\": false, \"sort\": {\"columnIndex\": null, \
         \"direction\": null}, \"showTotal\": false, \"totalFunc\": \"sum\"}, \
         \"aggs\": [{\"id\": \"1\", \"enabled\": true, \"type\": \"count\", \
         \"schema\": \"metric\", \"params\": {}}, {\"id\": \"2\", \
         \"enabled\": true, \"type\": \"filters\", \"schema\": \"bucket\", \
         \"params\": {\"filters\": []}}]}",
         "visualisation_with_valid_values.json"),
        ("/",
         "{\"title\": \"[Generated] - /\", \"type\": \"table\", \"params\": \
          {\"perPage\": 20, \"showPartialRows\": false, \
          \"showMetricsAtAllLevels\": false, \"sort\": {\"columnIndex\": null,\
          \"direction\": null}, \"showTotal\": false, \"totalFunc\": \"sum\"},\
          \"aggs\": [{\"id\": \"1\", \"enabled\": true, \"type\": \"count\", \
          \"schema\": \"metric\", \"params\": {}}, {\"id\": \"2\", \
          \"enabled\": true, \"type\": \"filters\", \"schema\": \"bucket\", \
          \"params\": {\"filters\": []}}]}",
         "visualisation_with_empty_vis_state.json")
    ]
)
def test_generate_visualisation_integration(path_name, vis_state, expected):
    assert helpers.get_test_results_json_file(expected) == \
        visualisation.generate_visualisation(path_name, json.loads(vis_state))


@patch.object(visualisation, "set_vis_state")
@patch.object(visualisation, "set_title")
def test_generate_visualisation(set_title, set_vis_state):
    visualisation.generate_visualisation("path", {"vis_state"})
    assert set_title.call_count == 1
    assert set_vis_state.call_count == 1


def test_set_title_value_error():
    with raises(ValueError):
        visualisation.set_title(None)


@mark.parametrize(
    "path_name, expected",
    [
        ("Secret", "[Generated] - Secret"),
        ("fdsafd", "[Generated] - fdsafd")
    ]
)
def test_set_title(path_name, expected):
    visualisation.set_title(path_name)
    assert visualisation.visualisation['title'] == expected


def test_set_vis_state_value_error():
    with raises(ValueError):
        visualisation.set_vis_state(None)


@mark.parametrize(
    "vis_state, expected",
    [
        ({}, "{}"),
        ({"some": "stuff"}, "{\"some\": \"stuff\"}")
    ]
)
def test_set_vis_state(vis_state, expected):
    visualisation.set_vis_state(vis_state)
    assert visualisation.visualisation['visState'] == expected


# @mark.parametrize(
#     "project, key, vis_state, expected",
#     [
#         ("", "", {}, "visualisation_with_empty_vis_state.json"),
#         ("Secret", "Valid", {"some": "here"},
#          "visualisation_with_valid_values.json")
#     ]
# )
# def test_get(project, key, vis_state, expected):
#     assert get_test_results_json_file(expected) == \
#         Visualisation(project, key, vis_state).get()


# def get_test_results_json_file(name: str) -> dict:
#     with open(os.path.abspath(f"tests/unit/resources/" + name)) as file:
#         return json.loads(file.read())
