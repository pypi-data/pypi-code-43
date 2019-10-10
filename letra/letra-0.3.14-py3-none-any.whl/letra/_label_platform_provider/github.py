from letra import Label
from .github_helpers import check_github_api_response_for_errors, get_headers
from .http_helpers import request_json, HttpJsonResponse
from letra._parser import extract_labels


def get_base_label_api_url(owner: str, repository: str):
    return f"https://api.github.com/repos/{owner}/{repository}/labels"


async def get_labels_from_repository(
    owner: str, repository: str, token: str = ""
):
    base_url = get_base_label_api_url(owner, repository)
    url = f"{base_url}?per_page=100"
    headers = get_headers(token)
    response = await request_json(url=url, http_verb="get", headers=headers)
    check_github_api_response_for_errors(
        response=response,
        owner=owner,
        repository=repository,
        request_headers=headers,
    )
    labels = extract_labels({"labels": response.data})
    return labels


async def create_label(
    label: Label, owner: str, repository: str, token: str = ""
):
    url = get_base_label_api_url(owner, repository)
    headers = get_headers(token)
    data = {
        "name": label.name,
        "description": label.description,
        "color": label.color,
    }
    response = await request_json(
        url=url, http_verb="post", json=data, headers=headers
    )
    check_github_api_response_for_errors(
        response=response,
        owner=owner,
        repository=repository,
        request_headers=headers,
    )
