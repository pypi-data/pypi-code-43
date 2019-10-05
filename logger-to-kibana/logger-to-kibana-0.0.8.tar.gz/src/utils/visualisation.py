"""
This module handles the Kibana Visualisation generation
"""
import configparser
import json

config = configparser.ConfigParser()
config.read("settings.ini")

index = config.get('kibana', 'Index')

visualisation = {"title": "" "visState"}
kibana_meta = {
    "searchSourceJSON": json.dumps(
        {
            "index": index,
            "query": {"query": "", "language": "lucene"},
            "filter": [],
        }
    )
}


def generate_visualisation(folder_name: str, vis_state: dict) -> dict:
    set_title(folder_name)
    set_vis_state(vis_state)
    visualisation["kibanaSavedObjectMeta"] = kibana_meta
    return visualisation


def set_title(path_name: str):
    if not isinstance(path_name, str):
        raise ValueError("path_name should be a string")
    visualisation["title"] = "[Generated] - " + path_name


def set_vis_state(vis_state: dict):
    if not isinstance(vis_state, dict):
        raise ValueError("vis_state should be a dict")
    visualisation["visState"] = json.dumps(vis_state)
