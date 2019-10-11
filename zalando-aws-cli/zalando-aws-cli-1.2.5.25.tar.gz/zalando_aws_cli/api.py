import boto3.session
import configparser
import jwt
import os
import requests
import stups_cli.config
import zign.api

from collections import namedtuple

CONFIG_NAME = 'zalando-aws-cli'

AWSRole = namedtuple('AWSRole', ['account_id', 'account_name', 'role_name'])
AWSCredentials = namedtuple('AWSCredentials', ['access_key_id', 'secret_access_key', 'session_token'])


def load_config():
    '''Load the configuration from the default location'''
    return stups_cli.config.load_config(CONFIG_NAME)


def config_service_url():
    '''Return the AWS Credentials Service URL from configuration'''
    return load_config()['service_url']


def store_config(config):
    '''Store the updated configuration to the default location'''
    stups_cli.config.store_config(config, CONFIG_NAME)


def get_token():
    '''Generate a new Zalando access token'''
    return zign.api.get_token_implicit_flow('zaws')['access_token']


def get_username(token):
    '''Get the username from a Zalando access token'''
    decoded_token = jwt.decode(token, verify=False)
    try:
        return decoded_token['https://identity.zalando.com/managed-id']
    except KeyError:
        raise KeyError('Invalid token. Please check your ztoken configuration')


def get_roles(token, service_url=None):
    '''Get the list of all available roles'''

    if not service_url:
        service_url = config_service_url()

    username = get_username(token)
    url = "{}/aws-account-roles/{}".format(service_url, username)

    response = requests.get(url, headers={'Authorization': 'Bearer {}'.format(token)}, timeout=30)
    response.raise_for_status()

    roles = response.json()['account_roles']
    return [AWSRole(role['account_id'], role['account_name'], role['role_name']) for role in roles]


def get_credentials(token, account_id, role_name, service_url=None):
    '''Generate new AWS credentials for the provided AWS account ID and role name'''
    if not service_url:
        service_url = config_service_url()

    url = "{}/aws-accounts/{}/roles/{}/credentials".format(service_url, account_id, role_name)

    response = requests.get(url, headers={'Authorization': 'Bearer {}'.format(token)}, timeout=30)
    response.raise_for_status()

    result = response.json()
    return AWSCredentials(access_key_id=result['access_key_id'],
                          secret_access_key=result['secret_access_key'],
                          session_token=result['session_token'])


def env_vars(credentials):
    '''Return the environment variables for configuring AWS SDK with the provided credentials'''
    return {'AWS_ACCESS_KEY_ID': credentials.access_key_id,
            'AWS_SECRET_ACCESS_KEY': credentials.secret_access_key,
            'AWS_SESSION_TOKEN': credentials.session_token}


def persist_credentials(credentials, profile_name):
    '''Persist the AWS credentials for later use by the AWS SDK'''

    credentials_path = os.path.expanduser('~/.aws/credentials')
    os.makedirs(os.path.dirname(credentials_path), exist_ok=True)

    config = configparser.ConfigParser()
    if os.path.exists(credentials_path):
        config.read(credentials_path)

    config[profile_name] = {'aws_access_key_id': credentials.access_key_id,
                            'aws_secret_access_key': credentials.secret_access_key}

    if credentials.session_token:
        # apparently the different AWS SDKs either use "session_token" or "security_token", so set both
        config[profile_name]['aws_session_token'] = credentials.session_token
        config[profile_name]['aws_security_token'] = credentials.session_token

    with open(credentials_path, 'w') as fd:
        config.write(fd)


def boto3_session(credentials, region_name=None):
    '''Create a new boto3 Session with the provided credentials'''
    return boto3.session.Session(aws_access_key_id=credentials.access_key_id,
                                 aws_secret_access_key=credentials.secret_access_key,
                                 aws_session_token=credentials.session_token,
                                 region_name=region_name)
