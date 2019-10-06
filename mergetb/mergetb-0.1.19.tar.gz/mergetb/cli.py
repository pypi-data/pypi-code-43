import getpass
import logging
import time
from os.path import expanduser, dirname
from os import environ
from pathlib import Path

import requests
import yaml

log = logging.getLogger(__name__)

class MergeApiCliException(Exception):
    pass


def request_token_to(token_path, username, password):
    '''Request a client access token and save to token_path '''
    dp = Path(dirname(token_path))
    if not dp.exists():
        dp.mkdir(parents=True)

    token, exp = request_token(username, password)

    with Path(token_path).open(mode='w') as fd:
        log.debug('dumping token to %s', token_path)
        yaml.dump(
            {
                'token': token,
                'expires_at': time.time()+exp,
                'user': username,
            },
            fd
        )

def request_token(username, password):
    '''Request a client access token. If username and/or
       password are None or not given, they will be asked
       for.
    '''
    uid = username if username else getpass.getuser()
    pw = password if password else getpass.getpass()
    log.info('Getting access token for %s', username)

    try:
        req = requests.post(
            'https://mergetb.auth0.com/oauth/token',
            headers={
                'Content-Type': 'application/json',
            },
            json={
                'username': uid,
                'password': pw,
                'client_id': 'opDBVn3y2Ez4g43c128hDvEaaO6si0na',
                'audience': 'https://mergetb.net/api/v1',
                'realm': 'Username-Password-Authentication',
                'grant_type': 'password',
                'scope': 'profile openid email',
                'device': '',
            }
        )
        req.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if req.status_code == 403:
            m = 'Login failure. Bad password.\n(HTTP Error: {})'.format(e)
        elif req.status_code == 429:
            m = ('Auth0 has too many recent requests. Please wait '
                 'a minute and try again.')
        else:
            m = 'request error: {}'.format(e)
        log.critical(m)
        raise MergeApiCliException(m)
    except requests.exceptions.RequestException as e:
        m = 'error getting authorization token: {}'.format(e)
        log.critical(e)
        raise MergeApiCliException(m)

    body = req.json()
    log.debug('resp body: %s', body)
    # Make sure all the keys we want are there...
    if not all(k in body for k in ('access_token', 'expires_in', 'token_type')):
        m = 'Expected fields not found in token response.'
        log.critical(m)
        raise MergeApiCliException(m)

    if body['token_type'] != 'Bearer':
        m = 'bad token_type in access token: {}'.format(body['token_type'])
        log.critical(m)
        raise MergeApiCliException(m)

    return body['access_token'], body['expires_in']


class CliToken():
    def __init__(self, token_path=None, apicert_path=None):
        if not token_path:
            self.token_path = Path(expanduser("~")+"/.merge/cli_token")
        else:
            self.token_path = Path(token_path)

        self.prev_ca_bundle = None
        if apicert_path:
            self.apicert = apicert_path
        elif 'MERGE_API_CERT' in environ:
            self.apicert = environ['MERGE_API_CERT']
        else:
            self.apicert = None

    def __enter__(self):
        token = self.get_cli_token()

        if self.apicert:
            if 'REQUESTS_CA_BUNDLE' in environ:
                self.prev_ca_bundle = environ['REQUESTS_CA_BUNDLE']
                log.info('Setting REQUESTS_CA_BUNDLE to %s', self.apicert)

            environ['REQUESTS_CA_BUNDLE'] = self.apicert

        return token

    def __exit__(self, *args):
        # Do we want to blow away the token? Or just do nothing here?
        # "for now", do nothing
        if self.prev_ca_bundle:
            environ['REQUESTS_CA_BUNDLE'] = self.prev_ca_bundle
            self.prev_ca_bundle = None

    # Get the client token directly.
    def get_cli_token(self, retries=2):
        if retries <= 0:
            log.warning('Could not get client token after all retries.')
            return None

        with self.token_path.open() as fd:
            try:
                token = yaml.safe_load(fd)
            except yaml.YAMLError as e:
                m = 'Unable to parge cli token file at {}: {}'.format(self.token_path, e)
                log.critical(m)
                raise MergeApiCliException(m)

            # check expiry and possibly, re-request.
            if token['expires_at'] < time.time():
                log.info('token expired, requesting new one.')
                request_token_to(self.token_path, token['user'], None)
                return self.get_cli_token(retries-1)

        return token['token']
