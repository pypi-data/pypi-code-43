from collections import defaultdict
from datetime import date
from typing import List

import yaml


def answers_to_yaml(answers: dict) -> str:
    structured_dict = answers_to_structured_dict(answers)
    yaml = structured_dict_to_yaml(structured_dict)
    return yaml


def answers_to_structured_dict(answers: dict) -> dict:
    def nested_dict() -> defaultdict:
        return defaultdict(nested_dict)

    def default_to_dict(d) -> dict:
        if isinstance(d, defaultdict):
            d = {k: default_to_dict(v) for k, v in d.items()}
        return d

    output = nested_dict()

    if answers["ignore"] == "true":
        output["meta"]["ignore"] = yaml_str(answers["ignore"])
        return default_to_dict(output)

    output["name"] = answers["name"]
    output["status"] = answers["status"]
    output["meta"]["ignore"] = yaml_str(answers["ignore"])
    output["ownership"]["owner"] = answers["owner"]
    output["ownership"]["maintainers"] = comma_sep(answers["maintainers"])
    output["public-info"]["reach"] = answers["reach"]
    if answers["tech-implementation"] != "null":
        output["public-info"]["tech-implementation"] = yaml_str(
            answers["tech-implementation"]
        )
    if answers.get("client-ids_list"):
        client_ids = list(map(int, answers["client-ids_list"]))
        output["public-info"]["client-ids"] = client_ids
    if answers.get("client-ids_str"):
        client_ids = list(map(int, comma_sep(answers["client-ids"])))
        output["public-info"]["client-ids"] = client_ids
    if answers.get("release-date"):
        release_date = date.fromisoformat(answers["release-date"])
        output["public-info"]["release-date"] = release_date
    if answers.get("tags"):
        output["public-info"]["tags"] = answers["tags"]
    output["public-info"]["departments"] = answers["departments"]
    output["public-info"]["platforms"] = answers["platforms"]
    if answers.get("wiki"):
        output["public-info"]["documentation"]["wiki"] = answers["wiki"]
    if answers.get("cards"):
        output["public-info"]["documentation"]["cards"] = answers["cards"]
    if answers.get("spreadsheets"):
        output["public-info"]["documentation"]["spreadsheets"] = answers["spreadsheets"]
    if answers.get("docs"):
        output["public-info"]["documentation"]["docs"] = answers["docs"]
    if answers.get("trackable"):
        output["tech-info"]["trackable"] = yaml_str(answers["trackable"])
    if answers.get("documentation"):
        output["tech-info"]["documentation"] = answers["documentation"]
    if answers.get("deployments"):
        output["deployments"] = deployments_list(answers)
    return default_to_dict(output)


def structured_dict_to_yaml(structured_dict: dict) -> str:
    return yaml.dump(structured_dict, sort_keys=False)


def comma_sep(input: str) -> list:
    return [i.strip() for i in input.split(",")]


def deployments_list(answers: dict) -> list:
    deployments_dict = {x: {} for x in answers["deployments"]}
    for key, value in answers.items():
        if "deployments." in key:
            key_parts = key.split(".")
            if key_parts[2] in ["run-name", "schedule", "trigger"]:
                set_run_value(deployments_dict, key_parts, value)
            else:
                set_normal_value(deployments_dict, key_parts, value)

    deployments_list: List[dict] = []
    for key, value in deployments_dict.items():
        deployment = {"type": key}
        deployment.update(value)
        deployments_list.append(deployment)
    return deployments_list


def set_run_value(deployments_dict: dict, key_parts: list, value: str) -> None:
    deployments_dict[key_parts[1]].setdefault("runs", [{}])[0][key_parts[2]] = value


def set_normal_value(deployments_dict: dict, key_parts: list, value: str) -> None:
    deployments_dict[key_parts[1]][key_parts[2]] = value


def yaml_str(value: str):
    return bool(value) if value in ("true", "false") else value
