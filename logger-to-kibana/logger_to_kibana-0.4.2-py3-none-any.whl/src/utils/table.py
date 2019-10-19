import copy

group_filter = {"input": {"query": ""}, "label": ""}
vis_state = {
    "title": "",
    "type": "table",
    "params": {
        "perPage": 20,
        "showPartialRows": False,
        "showMetricsAtAllLevels": False,
        "sort": {
            "columnIndex": None,
            "direction": None
        },
        "showTotal": False,
        "totalFunc": "sum"
    },
    "aggs": [
        {
            "id": "1",
            "enabled": True,
            "type": "count",
            "schema": "metric",
            "params": {}
        },
        {
            "id": "2",
            "enabled": True,
            "type": "filters",
            "schema": "bucket",
            "params": {"filters": []},
        }
    ]
}


def generate_table_vis_state(path_name, logs) -> dict:
    set_title(path_name)
    set_logs(logs)
    return vis_state


def set_title(path_name: str):
    if not isinstance(path_name, str):
        raise ValueError("path_name must be a string")
    vis_state["title"] = f"[Generated] - {path_name}"


def set_logs(logs: []):
    vis_state["aggs"][1]["params"]["filters"] = []
    if logs:
        for log in logs:
            group_filter["input"]["query"] = log["query"]
            group_filter["label"] = log["label"]
            vis_state["aggs"][1]["params"]["filters"].append(
                copy.deepcopy(group_filter)
            )
