""" Module for interacting with AWS ECR """
from base64 import b64decode

# pylint: disable=import-error
import boto3

import bwdt.lib.auth
from bwdt.lib.envvar import env


# pylint: disable=too-few-public-methods
class ECR(object):
    """ Class for interacting with AWS ECR """
    def __init__(self):
        auth = bwdt.lib.auth.get()
        session = boto3.Session(aws_access_key_id=auth['key_id'],
                                aws_secret_access_key=auth['key'])
        region = env()['region']
        client = session.client('ecr', region_name=region)
        token = client.get_authorization_token()
        b64token = token['authorizationData'][0]['authorizationToken']
        decoded_token = b64decode(b64token)
        token_data = decoded_token.split(':')
        username = token_data[0]
        password = token_data[1]
        registry = token['authorizationData'][0]['proxyEndpoint']
        self.credentials = {'username': username, 'password': password,
                            'registry': registry}
        self.client = client

    def registry_prefix(self):
        """ Return the registry URL """
        prefix = self.credentials['registry'].replace('https://', '')
        prefix = prefix.replace('http://', '')
        return prefix
