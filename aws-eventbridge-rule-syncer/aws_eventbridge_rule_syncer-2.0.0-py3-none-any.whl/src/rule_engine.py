import json


# This method applies all the rules to an event and return a list of
# targets to which the event belongs
def rule_engine(event, rules):

    # Event Detail is a JSON string. Needs to be converted to Dict.
    event["Detail"] = json.loads(event["Detail"])
    targets = []
    for rule in rules:
        pattern = rule["pattern"]
        target = rule["target"]
        event_lower_case = {
            "detail-type": event["DetailType"],
            "detail": event["Detail"],
            "source": event["Source"],
            "resources": event["Resources"] if "Resources" in event else None,
            "time": event["Time"] if "Time" in event else None,
        }

        if match_pattern(pattern, event_lower_case):
            targets.append(target)

    return targets


"""
This method matches an event against a pattern according to AWS Event Bridge
Pattern matching
Check this for more information:
https://docs.aws.amazon.com/eventbridge/latest/userguide/eventbridge-and-event-patterns.html
"""
# TODO Handling numbers at string level
def match_pattern(pattern, event):
    for key, value in pattern.items():
        if key not in event:
            return False

        if type(value) is list:
            if type(event[key]) is dict:
                return False

            if type(event[key]) is not list and event[key] not in value:
                return False

            # Handling Arrays in EventBridge Event Patterns
            if type(event[key]) is list:
                # Check for array intersection
                intersection = set(value) & set(event[key])
                if not intersection:
                    return False

        elif type(value) is dict:
            if type(event[key]) is not dict:
                return False

            if not match_pattern(value, event[key]):
                return False
        else:
            print(
                "Invalid pattern {}, {} should be a list or "
                "dict".format(pattern, value)
            )
            return False

    return True
