"""
This function handles the generation of the kibana visualisation
"""
from src.configuration import config

import json
import requests
from src.utils import visualisation, table


def generate_and_send_visualisation(folder_name: str, items: []):
    vis = generate_folder_visualisation(folder_name, items)
    send_visualisation(folder_name, vis)


def generate_folder_visualisation(folder_name: str, items: []) -> dict:
    vis_state = table.generate_table_vis_state(folder_name, items)
    return visualisation.generate_visualisation(folder_name, vis_state)


def send_visualisation(folder_name: str, visualisation: dict):
    headers = {"kbn-xsrf": "true"}
    data = {"attributes": visualisation}
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
