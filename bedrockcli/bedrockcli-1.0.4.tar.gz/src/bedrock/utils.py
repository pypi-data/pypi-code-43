#!/usr/bin/env python3

import os
from os.path import expanduser


def init_path(path):
    os.makedirs(expanduser(f'~/.bedrock/{path}'), exist_ok=True)


def append_env(environment, env_var, warn_missing=False):
    if env_var in os.environ:
        environment.append(f'{env_var}={os.environ[env_var]}')
    elif warn_missing:
        print(f'** WARNING - Missing environment variable: {env_var}')

