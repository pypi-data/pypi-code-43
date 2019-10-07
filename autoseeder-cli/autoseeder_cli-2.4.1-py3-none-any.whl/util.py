import requests
import sys
import os
try:
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urljoin

from loguru import logger


class EnvVarException(Exception):
    pass


ENV_VAR_DEFS = {
    'base_url': 'AUTOSEEDER_BASE_URL',
    'token': 'AUTOSEEDER_TOKEN',
    'user': 'AUTOSEEDER_USER',
    'pass': 'AUTOSEEDER_PASS',
}


def process_env_args(token_auth_vars=True):
    env_vars = {}

    for ev, k in ENV_VAR_DEFS.items():
        try:
            env_vars['{}'.format(ev)] = os.environ[k]
        except KeyError:
            pass

    try:
        if not env_vars.get('base_url'):
            raise EnvVarException('{}'.format(ENV_VAR_DEFS['base_url']))
        if not token_auth_vars and not env_vars.get('user'):
            raise EnvVarException('{}'.format(ENV_VAR_DEFS['user']))
        if not token_auth_vars and not env_vars.get('pass'):
            raise EnvVarException('{}'.format(ENV_VAR_DEFS['pass']))
        elif token_auth_vars and not env_vars.get('token'):
            raise EnvVarException('{}'.format(ENV_VAR_DEFS['token']))
    except EnvVarException as e:
        raise RuntimeError('You need to set environment variable(s): {}'.format(e))

    return env_vars


def api_login(root, username, password):
    path = urljoin(root, 'api/v0/login/')
    logger.debug(path)
    d = {'username': username, 'password': password}
    r = requests.post(path, data=d)

    logger.debug(r)

    if r.status_code != 200:
        raise Exception('Unhandled response from login API endpoint: {}'.format(r.content))

    return r.json()['token']


def api_logout(root, token):
    path = urljoin(root, 'api/v0/logout/')
    h = {'Authorization': 'Token ' + token}
    r = requests.post(path, headers=h)

    if r.status_code != 204:
        raise Exception('Unhandled response from logout API endpoint: {}'.format(r.content))


def init_logger():
    level = os.environ.get("AUTOSEEDER_LOG_LEVEL", "ERROR")

    # remove the default stderr logger with its debug level
    # discussion at https://github.com/Delgan/loguru/issues/51
    logger.remove()
    logger.add(sys.stderr, level=level)

    return logger


logger = init_logger()
