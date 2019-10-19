"""
This function handles the generation of the kibana visualization
"""
from src.configuration import config

import json
import requests
from src.utils import visualization
from itertools import groupby


def generate_and_send_visualizations(folder_name: str, items: []):
    grouped_items = group_items(items)
    if grouped_items:
        for group in grouped_items:
            title = get_title_from_group(folder_name, group[0])
            vis = generate_folder_visualization(title, group)
            send_visualization(title, vis)


def get_title_from_group(folder_name: str, group: dict) -> str:
    return (f"{folder_name} {group['subfolder']} "
            f"{group['filename']} {group['function']}")


def generate_folder_visualizations(folder_name: str, items: []) -> []:
    result = []
    grouped_items = group_items(items)
    if grouped_items:
        for group in grouped_items:
            title = get_title_from_group(folder_name, group[0])
            result.append(generate_folder_visualization(title, group))
    return result


def group_items(items: []) -> []:
    groups = []
    sortedreader = sorted(items, key=lambda d:
                          (d['subfolder'], d['filename'], d['function']))
    for k, g in groupby(sortedreader, key=lambda d:
                        (d['subfolder'], d['filename'], d['function'])):
        groups.append(list(g))
    return groups


def generate_folder_visualization(folder_name: str, items: []) -> dict:
    return visualization.generate_visualization(folder_name, items)


def send_visualization(folder_name: str, visualization: dict):
    headers = {"kbn-xsrf": "true"}
    data = {"attributes": visualization}
    url = (
        f"""{config.kibana.BaseUrl}/api/saved_objects/visualization/"""
        f"""generated-{folder_name}?overwrite=true"""
    )

    response = requests.post(
        url,
        headers=headers,
        data=json.dumps(data),
    )
    print(response.text)
