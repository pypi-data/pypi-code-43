import requests
import shelve

name_id_seperator = "➖   "


def values(name: str, token: str) -> list:
    if name == "client":
        return client(token)
    elif name == "deployment":
        return deployment()
    else:
        try:
            values_list = sesame_list(token, name)
        except requests.RequestException:
            with shelve.open("lists") as lists:
                values_list = lists.get(name, [])
        with shelve.open(name) as lists:
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

        clients = [client_name_format(client) for client in response.json()]
        return sorted(clients)
    except Exception:
        return ["None found."]


def client_name_format(client: dict) -> str:
    return client["name"].ljust(50) + name_id_seperator + client["id"]
