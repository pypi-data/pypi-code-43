from datetime import date
from typing import Dict, List, Union

import yaml

from blyaml.tree import Tree


def answers_to_yaml(answers: dict) -> str:
    structured_dict = answers_to_structured_dict(answers)
    yaml = structured_dict_to_yaml(structured_dict)
    return yaml


def answers_to_structured_dict(answers: dict) -> dict:
    output = Tree()

    if answers["ignore"] == "true":
        output["meta"]["ignore"] = yaml_str(answers["ignore"])
        return output.as_dict()

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
        # Convert to date object to avoid quotes in yaml
        release_date = date.fromisoformat(answers["release-date"])
        output["public-info"]["release-date"] = release_date
    if answers.get("tags"):
        output["public-info"]["tags"] = answers["tags"]
    output["public-info"]["departments"] = answers["departments"]
    output["public-info"]["platforms"] = answers["platforms"]
    if answers.get("wiki"):
        output["public-info"]["documentation"]["wiki"] = comma_sep(answers["wiki"])
    if answers.get("cards"):
        output["public-info"]["documentation"]["cards"] = comma_sep(answers["cards"])
    if answers.get("spreadsheets"):
        output["public-info"]["documentation"]["spreadsheets"] = comma_sep(
            answers["spreadsheets"]
        )
    if answers.get("docs"):
        output["public-info"]["documentation"]["docs"] = comma_sep(answers["docs"])

    if answers.get("trackable"):
        output["tech-info"]["trackable"] = yaml_str(answers["trackable"])
    if answers.get("documentation"):
        output["tech-info"]["documentation"] = comma_sep(answers["documentation"])

    if answers.get("deployments"):
        output["deployments"] = deployments_list(answers)
    return output.as_dict()


def comma_sep(input: str) -> list:
    """Convert a comma seperated string into a list."""
    return [i.strip() for i in input.split(",")]


def deployments_list(answers: dict) -> list:
    """Find all deployment answers and creates and returns a deployments list."""
    deployments_dict: Dict[str, dict] = {x: {} for x in answers["deployments"]}
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
    """Create 'runs' list of dicts if it does not exist."""
    deployments_dict[key_parts[1]].setdefault("runs", [{}])[0][key_parts[2]] = value


def set_normal_value(deployments_dict: dict, key_parts: list, value: str) -> None:
    deployments_dict[key_parts[1]][key_parts[2]] = value


def structured_dict_to_yaml(structured_dict: dict) -> str:
    return yaml.dump(data=structured_dict, sort_keys=False)


def yaml_str(value: str) -> Union[bool, str]:
    """Convert true and false into bool, so that they do not get quoted in yaml."""
    if value == "true":
        return True
    elif value == "false":
        return False
    else:
        return value
