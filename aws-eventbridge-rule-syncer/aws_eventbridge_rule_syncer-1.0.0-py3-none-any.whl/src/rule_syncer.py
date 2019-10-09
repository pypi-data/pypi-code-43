# -*- coding: utf-8 -*-
import json

import boto3

sqs_client = boto3.resource("sqs")
event_client = boto3.client("events")

# { "name": (pattern, description, target, state)}
rules_map = dict()


def sync_rules(rules_path, prefix, backup_file):

    # Backup existing rules to a file
    backup_rules(backup_file)

    with open(rules_path, "r") as f:
        rules = json.load(f)

    for rule in rules:
        # name should be unique for every rule
        name = rule["name"]
        pattern = rule["pattern"]
        description = rule["description"]
        target = rule["target"]
        state = rule["state"]
        rules_map[prefix + name] = (pattern, description, target, state)

    aws_rules = get_rules_from_aws(prefix)

    # Delete rules from AWS which are not present
    for aws_rule in aws_rules:
        if aws_rule not in rules_map.keys():
            # Get the targets for the rule
            targets = get_target_ids_for_rule(aws_rule)

            # Remove targets first from rule
            remove_targets(aws_rule, targets)

            # Delete rule from AWS
            delete_rule_from_aws(aws_rule)

    # Create/Update for other rules
    for key in rules_map.keys():
        val = rules_map[key]

        name = key
        pattern = val[0]
        description = val[1]
        target = val[2]
        state = val[3]

        # Create/update Queue
        target_arn = sync_queue(prefix + target)
        # Create rule
        create_rule(name, pattern, description, target_arn, state)
        # Set target
        put_target(name, target, target_arn)


def backup_rules(backup_file):
    try:
        res = event_client.list_rules()
    except Exception as ex:
        raise Exception("Exception occurred while calling list_rules() API: {"
                        "}", ex)

    if res.get("ResponseMetadata", {}).get("HTTPStatusCode", 502) != 200:
        raise Exception("Invalid response from list_rules() API")

    rules = []
    for rule in res.get("Rules"):
        name = rule["Name"]
        targets = get_targets_for_rule(name)

        entry = {
            "Rule": rule,
            "Targets": targets
        }

        rules.append(entry)

    with open(backup_file, "w") as f:
        data = json.dumps(rules)
        f.write(data)

    print("Rules backed up in ", backup_file)


def get_rules_from_aws(prefix):
    res = event_client.list_rules(NamePrefix=prefix)

    if res.get("ResponseMetadata", {}).get("HTTPStatusCode", 502) != 200:
        raise Exception("Invalid response from list_rules() API")

    rules = res.get("Rules")
    names = []
    for rule in rules:
        names.append(rule["Name"])

    return names


def delete_rule_from_aws(name):
    res = event_client.delete_rule(Name=name)

    if res.get("ResponseMetadata", {}).get("HTTPStatusCode", 502) != 200:
        raise Exception("Error occurred while deleting rule: {}", name)

    print("Rule deleted: ", name)


def sync_queue(name):
    try:
        res = sqs_client.create_queue(QueueName=name)
        print("Queue created: ", name)

        return res.attributes["QueueArn"]
    except Exception as ex:
        print("create_queue() queue: {} error: {}".format(name, ex))
        raise ex


def get_target_ids_for_rule(name):
    res = event_client.list_targets_by_rule(Rule=name)

    if res.get("ResponseMetadata", {}).get("HTTPStatusCode", 502) != 200:
        raise Exception(
            "Error occurred in get_target_ids_for_rule() rule: {}".format(name)
        )

    targets = []
    for target in res.get("Targets"):
        targets.append(target["Id"])

    print("Targets for rule {}: {}".format(name, targets))

    return targets


def get_targets_for_rule(name):
    try:
        res = event_client.list_targets_by_rule(Rule=name)
    except Exception as ex:
        raise Exception(
            "Error occurred in get_targets_for_rule() rule: {}".format(name)
        )

    if res.get("ResponseMetadata", {}).get("HTTPStatusCode", 502) != 200:
        raise Exception(
            "Error occurred in get_targets_for_rule() rule: {}".format(name)
        )

    return res.get("Targets")


def create_rule(name, pattern, description, q_arn, state):
    pattern = json.dumps(pattern)
    res = event_client.put_rule(
        Name=name, EventPattern=pattern, State=state, Description=description
    )

    if res.get("ResponseMetadata", {}).get("HTTPStatusCode", 502) != 200:
        raise Exception("Error occurred in put_rule() rule: {}".format(name))

    print("Rule created: ", name)


def put_target(rule, q_name, q_arn):
    res = event_client.put_targets(
        Rule=rule,
        Targets=[
            {
                # Using queue name as the Id. This will be used in
                # remove_target() call
                "Id": q_name,
                "Arn": q_arn,
                "InputPath": "$.detail",
            }
        ],
    )

    if res.get("ResponseMetadata", {}).get("HTTPStatusCode", 502) != 200:
        raise Exception("Error occurred in put_targets() for rule: {}".format(rule))

    print("Target updated for rule: ", rule)


def remove_targets(rule, targets):
    res = event_client.remove_targets(Rule=rule, Ids=targets)

    if res.get("ResponseMetadata", {}).get("HTTPStatusCode", 502) != 200:
        raise Exception("Error occurred in remove_targets() for rule: {}".format(rule))
