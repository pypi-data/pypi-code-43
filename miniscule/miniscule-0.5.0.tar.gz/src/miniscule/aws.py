import logging
import json
import boto3
import botocore

log = logging.getLogger(__name__)


def _secrets_manager_client():
    return boto3.client('secretsmanager')


def secrets_manager_constructor(loader, node):
    friendly_name = loader.construct_yaml_str(node)
    client = _secrets_manager_client()

    secret_string = None
    try:
        response = client.get_secret_value(SecretId=friendly_name)
        secret_string = response.get('SecretString')
    except botocore.exceptions.ClientError as exc:
        log.warning(
            'Unable to obtain secrets manager value for %s: %s', friendly_name,
            exc)
        return None
    return _maybe_parse_secret_string(secret_string)


def _maybe_parse_secret_string(secret_string):
    if secret_string is None:
        return None
    return _maybe_parse_as_json(secret_string) or secret_string


def _maybe_parse_as_json(secret_string):
    try:
        return json.loads(secret_string)
    except json.JSONDecodeError:
        return None
