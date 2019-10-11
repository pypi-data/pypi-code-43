import requests
import shelve
from pathlib import Path


DIRECTROY = ".blyaml"


def values(name: str, token: str) -> list:
    shelf_pathname = str(Path.home() / DIRECTROY / "lists")
    try:
        if name == "client":
            values_list = client(token)
        elif name == "deployment":
            values_list = deployment()
        else:
            values_list = sesame_list(token, name)
    except requests.RequestException:
        with shelve.open(shelf_pathname) as lists:
            values_list = lists[name]
    with shelve.open(shelf_pathname) as lists:
        lists[name] = values_list
    return values_list


def sesame_list(token: str, endpoint: str) -> list:
    sesame_api_url = f"https://sesame.brainlabsdigital.com/api/{endpoint}"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(sesame_api_url, headers=headers)

    try:
        assert response.status_code == 200
        return sorted([i["name"] for i in response.json()])
    except Exception:
        raise requests.RequestException


def deployment() -> list:
    return [
        "server-cronjob",
        "tech-managed-google-ads-script",
        "user-managed-google-ads-script",
        "server-button-press",
        "web-app",
        "tech-managed-apps-script",
        "user-managed-apps-script",
        "command-line",
        "glitch",
        "aws-lambda-function",
        "pepper",
    ]


def client(token: str) -> list:
    try:
        sesame_api_url = f"https://sesame.brainlabsdigital.com/api/client"
        headers = {"Authorization": f"token {token}"}
        response = requests.get(sesame_api_url, headers=headers)
        assert response.status_code == 200

        clients = [client_name_format(i) for i in response.json()]
        return sorted(clients, key=lambda d: d["name"])
    except Exception:
        raise requests.RequestException


def client_name_format(client_name_id: dict) -> dict:
    return {
        "name": client_name_id["name"].ljust(50) + client_name_id["id"],
        "value": client_name_id["id"],
    }
