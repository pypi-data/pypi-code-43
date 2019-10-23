import time

import boto3
import click

SUCCESSFUL_TERMINAL_STATES = ["CREATE_COMPLETE"]
PROBLEM_TERMINAL_STATES = [
    'CREATE_FAILED',
    "ROLLBACK_FAILED",
    "ROLLBACK_COMPLETE",
    "DELETE_FAILED",
    "DELETE_COMPLETE",
    "UPDATE_ROLLBACK_COMPLETE"
]

TERMINAL_STATES = SUCCESSFUL_TERMINAL_STATES + PROBLEM_TERMINAL_STATES


def get_cfn_client():
    return boto3.client('cloudformation')


def deploy_cfn_stack(stack_name, template_url, cfn_formatted_param_list):
    response = get_cfn_client().create_stack(
            StackName=stack_name,
            TemplateURL=template_url,
            Parameters=cfn_formatted_param_list,
            Capabilities=['CAPABILITY_NAMED_IAM'],
            OnFailure='DO_NOTHING',
            EnableTerminationProtection=False
    )
    return response["StackId"]


def get_cfn_outputs(stack_id, output_keys):
    stack_outputs = describe_cfn_stack(stack_id)["Outputs"]
    return {o["OutputKey"]: o["OutputValue"] for o in stack_outputs if o["OutputKey"] in output_keys}


def describe_cfn_stack(stack_id):
    """
    Output format documented at: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.describe_stacks
    """
    response = get_cfn_client().describe_stacks(StackName=stack_id)
    assert len(response["Stacks"]) == 1, f'Should be exactly one stack with Stack ID: {stack_id}'
    return response["Stacks"][0]



def display_cfn_stack_event(stack_event):
    """
    Stack event format available at: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.describe_stack_events
    """

    color = get_color_for_cfn_stack_event_type(stack_event['ResourceStatus'])
    fields_to_display = [
        fixed_widthify(stack_event['LogicalResourceId'], 40),
        fixed_widthify(stack_event['ResourceStatus'], 20)
    ]
    if 'ResourceStatusReason' in stack_event.keys():
        fields_to_display.append(stack_event['ResourceStatusReason'])

    line = "\t".join(fields_to_display)
    click.secho(line, fg=color)




def watch_cfn_stack_events_until_done(stack_id, session_log):
    """
    Query the CloudFormation API every 1 second. Log and display any new events
    """
    stack_events_seen = set()
    cfn_client = get_cfn_client()
    while True:
        events_to_display = []
        for event_page in cfn_client.get_paginator('describe_stack_events').paginate(StackName=stack_id):
            new_events = [event for event in event_page["StackEvents"] if event["EventId"] not in stack_events_seen]
            events_to_display.extend(new_events)

        events_to_display.reverse()  # Fix chronological order so newer events get printed later
        for event in events_to_display:
            session_log.log_cfn_event(logical_resource_id=event["LogicalResourceId"],
                                      resource_status=event['ResourceStatus'],
                                      resource_status_reason=event.get("ResourceStatusReason", None),
                                      timestamp=event["Timestamp"])
            display_cfn_stack_event(event)
            stack_events_seen.add(event['EventId'])

        stack_details = describe_cfn_stack(stack_id)
        stack_status = stack_details['StackStatus']
        if stack_status in TERMINAL_STATES:
            return stack_status, stack_details.get("StackStatusReason", None)
        time.sleep(1)



def convert_param_representation_to_cfn(param_dict):
    """
    Convert params from {"ParamName: "ParamVal", ...} format to the format expected by the CloudFormation API
    [{"ParameterKey": "ParamName", "ParameterValue": "ParamVal}, ...] correctly handling bools and optional params.
    """
    param_list = []
    for k, v in param_dict.items():
        if v is None:
            v = ""
        if isinstance(v, bool):
            v = str(v).lower()
        param_list.append({
            'ParameterKey': k,
            'ParameterValue': v
        })
    return param_list



def fixed_widthify(s, desired_width):
    if len(s) > desired_width:
        s = s[:desired_width - 3] + "..."
    else:
        add_width = desired_width - len(s)
        s = s + " " * add_width
    return s


def get_color_for_cfn_stack_event_type(event_status):
    """ Map CFN event status strings to red/green/blue colors (matching the CFN console) """

    if event_status in ["CREATE_IN_PROGRESS", "DELETE_IN_PROGRESS", "UPDATE_IN_PROGRESS"]:
        return 'blue'
    elif event_status in ["CREATE_COMPLETE", "DELETE_COMPLETE", "UPDATE_COMPLETE"]:
        return 'green'
    elif event_status in ["CREATE_FAILED", "DELETE_FAILED", "UPDATE_FAILED"]:
        return 'red'
    else:
        return 'black'
