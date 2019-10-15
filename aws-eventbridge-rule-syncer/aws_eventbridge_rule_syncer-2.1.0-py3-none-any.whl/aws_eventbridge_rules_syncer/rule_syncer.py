# -*- coding: utf-8 -*-
import json

import boto3

sqs_client = boto3.client("sqs")
event_client = boto3.client("events")

# { "name": (pattern, description, target, state)}
rules_map = dict()


def sync_rules(rules_path, backup_file, prefix, event_bus="default"):

    # Backup existing rules to a file
    backup_rules(backup_file, event_bus)

    with open(rules_path, "r") as f:
        rules = json.load(f)

    for rule in rules:
        # name should be unique for every rule
        name = rule["name"]
        pattern = rule["pattern"]
        description = rule["description"]
        target = rule["target"]
        state = rule["state"]
        queue = rule["queue"]

        rules_map[prefix + name] = (pattern, description, target, state, queue)

    aws_rules = get_rules_from_aws(event_bus, prefix)

    # Disable rules from AWS which are not present
    for aws_rule in aws_rules:
        if aws_rule not in rules_map.keys():
            disable_rule(aws_rule, event_bus)

    # Create/Update for other rules
    for key in rules_map.keys():
        val = rules_map[key]

        name = key
        pattern = val[0]
        description = val[1]
        target = val[2]
        state = val[3]
        queue = val[4]

        # Get Queue ARN
        queue_arn = get_queue_arn(queue)
        # Create rule
        create_rule(name, pattern, description, state, event_bus)
        # Set target
        put_target(name, event_bus, target, queue_arn)


def backup_rules(backup_file, event_bus):
    try:
        res = event_client.list_rules(EventBusName=event_bus)
    except Exception as ex:
        raise Exception("Exception occurred while calling list_rules() API: {"
                        "}", ex)

    if res.get("ResponseMetadata", {}).get("HTTPStatusCode", 502) != 200:
        raise Exception("Invalid response from list_rules() API")

    rules = []
    for rule in res.get("Rules"):
        name = rule["Name"]
        targets = get_targets_for_rule(name, event_bus)

        entry = {
            "Rule": rule,
            "Targets": targets
        }

        rules.append(entry)

    with open(backup_file, "w") as f:
        data = json.dumps(rules)
        f.write(data)

    print("Rules backed up in ", backup_file)


def get_rules_from_aws(event_bus, prefix):
    res = event_client.list_rules(EventBusName=event_bus, NamePrefix=prefix)

    if res.get("ResponseMetadata", {}).get("HTTPStatusCode", 502) != 200:
        raise Exception("Invalid response from list_rules() API")

    rules = res.get("Rules")
    names = []
    for rule in rules:
        names.append(rule["Name"])

    return names


def get_queue_arn(name):
    try:
        queue_url = get_queue_url(name)
        if queue_url is None:
            raise Exception("Queue URL not available for queue: {}", name)

        res = sqs_client.get_queue_attributes(
            QueueUrl=queue_url,
            AttributeNames=['QueueArn']
        )

        if res.get("ResponseMetadata", {}).get(
                "HTTPStatusCode", 502
        ) == 200 and res.get("Attributes", None):
            return res["Attributes"]['QueueArn']

    except Exception as ex:
        print("get_queue_attributes() queue: {} error: {}".format(name, ex))
        raise ex


def get_queue_url(name):
    try:
        response = sqs_client.get_queue_url(QueueName=name)
    except Exception as ex:
        # Throw an exception in case there is a failure retrieving
        # QueueUrl for Queue
        raise Exception(
            "Exception while retrieving QueueUrl for Queue: {}, "
            "Exception: {}".format(name, ex)
        )

    if response.get("ResponseMetadata", {}).get(
        "HTTPStatusCode", 502
    ) == 200 and response.get("QueueUrl", None):
        return response["QueueUrl"]
    else:
        return None


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


def get_targets_for_rule(name, event_bus):
    try:
        res = event_client.list_targets_by_rule(Rule=name, EventBusName=event_bus)
    except Exception as ex:
        raise Exception(
            "Error occurred in get_targets_for_rule() rule: {}".format(name)
        )

    if res.get("ResponseMetadata", {}).get("HTTPStatusCode", 502) != 200:
        raise Exception(
            "Error occurred in get_targets_for_rule() rule: {}".format(name)
        )

    return res.get("Targets")


def create_rule(name, pattern, description, state, event_bus):
    pattern = json.dumps(pattern)
    res = event_client.put_rule(
        Name=name, EventPattern=pattern, State=state,
        Description=description, EventBusName=event_bus
    )

    if res.get("ResponseMetadata", {}).get("HTTPStatusCode", 502) != 200:
        raise Exception("Error occurred in put_rule() rule: {}".format(name))

    print("Rule created: ", name)


def disable_rule(name, event_bus):
    res = event_client.disable_rule(Name=name, EventBusName=event_bus)

    if res.get("ResponseMetadata", {}).get("HTTPStatusCode", 502) != 200:
        raise Exception("Error occurred in disable_rule() rule: {}".format(
            name))

    print("Rule disabled: ", name)


def put_target(rule, event_bus, q_name, q_arn):
    res = event_client.put_targets(
        Rule=rule,
        EventBusName=event_bus,
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
