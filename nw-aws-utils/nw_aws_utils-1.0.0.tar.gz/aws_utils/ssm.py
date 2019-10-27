"""Functions for fetching parametes from SSM.
"""
import os
from boto3 import client as boto3_client
from botocore.exceptions import ClientError, NoCredentialsError, NoRegionError
from .exceptions import SsmError

def env_or_ssm(env_key, ssm_key, required=True):
    """Try to get an environmet variable first from env, then AWS SSM.
    Raises error if required is True.
    """
    value = os.environ.get(env_key)

    if value is None or value == "":
        try:
            value = get_ssm_parameter(ssm_key)
        except NoCredentialsError:
            pass


    if (value is None or value == "") and required:
        raise SsmError("Required setting undefined. Set {} in environment or "
                       "or {} in AWS SSM.".format(env_key, ssm_key))

    return value


def get_ssm_parameter(key):
    """Fetch value of an AWS SSM parameter.
    """
    try:
        ssm_client = boto3_client('ssm')
        resp = ssm_client.get_parameter(Name=key, WithDecryption=True)
        val = resp['Parameter']['Value']
    except (ClientError, NoRegionError) as e:
        val = None
    return val
