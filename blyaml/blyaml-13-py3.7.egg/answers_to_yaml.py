from collections import defaultdict
from typing import List

import yaml


def answers_to_yaml(answers: dict) -> str:
    structured_dict = answers_to_structured_dict(answers)
    yaml = structured_dict_to_yaml(structured_dict)
    return yaml


def answers_to_structured_dict(answers: dict) -> dict:
    output = defaultdict(dict)

    if answers["ignore"] == "true":
        output["meta"]["ignore"] = yaml_str(answers["ignore"])
        return dict(output)

    output["name"] = answers["name"]
    output["status"] = answers["status"]
    output["meta"]["ignore"] = yaml_str(answers["ignore"])
    output["ownership"]["owner"] = answers["owner"]
    output["ownership"]["maintainers"] = comma_sep_list(answers["maintainers"])
    output["public-info"]["reach"] = answers["reach"]
    if answers["tech-implementation"] != "null":
        output["public-info"]["tech-implementation"] = yaml_str(
            answers["tech-implementation"]
        )
    if answers.get("client-ids"):
        output["public-info"]["client-ids"] = comma_sep_list(answers["client-ids"])
    if answers.get("release-date"):
        output["public-info"]["release-date"] = answers["release-date"]
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
    return dict(output)


def structured_dict_to_yaml(structured_dict: dict) -> str:
    return yaml.dump(structured_dict, sort_keys=False)


def comma_sep_list(input: str) -> list:
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
