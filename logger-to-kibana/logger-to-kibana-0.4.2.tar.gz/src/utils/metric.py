import copy

metric_group_filter = {"input": {"query": ""}, "label": ""}
vis_state = {
    "title": "",
    "type": "metric",
    "params": {
        "addTooltip": True,
        "addLegend": False,
        "type": "metric",
        "metric": {
            "percentageMode": False,
            "useRanges": False,
            "colorSchema": "Green to Red",
            "metricColorMode": "None",
            "colorsRange": [{"from": 0, "to": 10000}],
            "labels": {"show": True},
            "invertColors": False,
            "style": {
                "bgFill": "#000",
                "bgColor": False,
                "labelColor": False,
                "subText": "",
                "fontSize": 60,
            },
        },
    },
    "aggs": [
        {
            "id": "1",
            "enabled": True,
            "type": "count",
            "schema": "metric",
            "params": {},
        },
        {
            "id": "2",
            "enabled": True,
            "type": "filters",
            "schema": "group",
            "params": {"filters": []},
        },
    ],
}


def generate_metric_vis_state(path_name, logs) -> dict:
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
            metric_group_filter["input"]["query"] = log["query"]
            metric_group_filter["label"] = log["label"]
            vis_state["aggs"][1]["params"]["filters"].append(
                copy.deepcopy(metric_group_filter)
            )
