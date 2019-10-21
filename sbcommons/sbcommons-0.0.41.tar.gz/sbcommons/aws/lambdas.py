import json
from typing import Dict

import boto3


def invoke(function_name: str, event: Dict, invocation_type: str = 'Event'):
    lambda_resource = boto3.client('lambda')
    return lambda_resource.invoke(
        FunctionName=function_name,
        InvocationType=invocation_type,
        Payload=json.dumps(event)
    )
