""" BWDT Authentication File functions """
import json
import sys
import os

import bwdt.lib.envvar


def get_dir_path():
    """ Return the path of the auth file's directory """
    env_auth_dir = bwdt.lib.envvar.env()['auth_dir']
    if env_auth_dir is not None:
        path = os.environ[env_auth_dir]
    else:
        base = os.path.expanduser("~")
        path = "{}/.breqwatr".format(base)
    return path


def get_file_path():
    """ Return the auth file path """
    directory = get_dir_path()
    file_path = '{}/auth.json'.format(directory)
    return file_path


def mkdir():
    """ Create the auth file path. Return true if created. """
    path = get_dir_path()
    exists = os.path.exists(path)
    if exists:
        return False
    try:
        os.mkdir(path)
    except OSError:
        return False
    return True


def get():
    """ Return the auth file content or None if it can't be opened """
    path = get_file_path()
    exists = os.path.exists(path)
    if not exists:
        return None
    try:
        with open(path, 'r') as auth_file:
            return json.load(auth_file)
    except (IOError, TypeError):
        return None


def set(key_id, key, offline, offline_path):
    """ Write the config file """
    data = {'key_id': key_id, 'key': key, 'offline': offline,
            'offline_path': offline_path}
    jdata = json.dumps(data, indent=4, sort_keys=True)
    jdata = jdata.rstrip()
    mkdir()
    filename = get_file_path()
    with open(filename, 'w+') as out_file:
        out_file.write(jdata)


def use_ecr():
    """ Return if ECR should be used, safely handing str values """
    try:
        data = get()
        return str(data['offline']).lower() == 'false'
    except TypeError:
        sys.stderr.write('ERROR: BWDT not configured / misconfigured\n')
        sys.exit()
