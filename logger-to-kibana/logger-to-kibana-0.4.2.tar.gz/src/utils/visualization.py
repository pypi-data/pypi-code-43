"""
This module handles the Kibana Visualization generation
"""
import json
from src.configuration import config
from src.utils import table, metric

visualization = {"title": "" "visState"}
kibana_meta = {
    "searchSourceJSON": json.dumps(
        {
            "index": config.kibana.Index,
            "query": {"query": "", "language": "lucene"},
            "filter": [],
        }
    )
}


def generate_visualization(title: str, items: []) -> dict:
    set_title(title)
    set_vis_state(generate_vis_state(title, items))
    visualization["kibanaSavedObjectMeta"] = kibana_meta
    return visualization


def generate_vis_state(title: str, items: []):
    if config.kibana.VisualizationType == 'metric':
        return metric.generate_metric_vis_state(title, items)
    return table.generate_table_vis_state(title, items)


def set_title(title: str):
    if not isinstance(title, str):
        raise ValueError("title should be a string")
    visualization["title"] = "[Generated] - " + title


def set_vis_state(vis_state: dict):
    if not isinstance(vis_state, dict):
        raise ValueError("vis_state should be a dict")
    visualization["visState"] = json.dumps(vis_state)
