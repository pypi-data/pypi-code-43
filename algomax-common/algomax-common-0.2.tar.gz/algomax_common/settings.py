import os
import sys
import json
from .terminal import FontColor
from .messages import PARAMS_REQUIRED

BASE_DIR = ''


def get_config(file_path: str):
    """
    get config data
    :param file_path: config file path
    :return: dict that contains config data
    """
    config_path = os.path.join(BASE_DIR, file_path)
    with open(config_path, 'r') as file_reader:
        config = json.loads(file_reader.read())
    return config


def get_settings_filename():
    """
    return settings filename from cli params
    :return: config filename
    """
    return sys.argv[1]


def get_settings():
    """
    return settings data
    :return: dict that contains config data
    """
    return get_config(get_settings_filename())


def get_params_filename():
    """
    return user algorithm params filename
    :return: params filename
    """
    if sys.argv[2] == 'None':
        # TODO: replace with logger
        print(FontColor.failed(PARAMS_REQUIRED))
        exit(0)

    return sys.argv[2]


def get_params():
    """
    return user algorithm params data
    :return: dict that contains params data
    """
    return get_config(get_params_filename())
