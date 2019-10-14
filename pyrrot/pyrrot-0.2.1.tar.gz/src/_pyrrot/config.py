import os

import yaml

from .constant import CALL_COUNT_PARAM, CONFIG_PARAM
from .schema import ConfigSchema


def read_configs(app, path):
    configs = []
    app.config[CALL_COUNT_PARAM] = {}
    absolute_path = _validate_path(path)
    print(absolute_path)
    if os.path.isfile(absolute_path):
        configs = _load_config(absolute_path)
    elif os.path.isdir(absolute_path):
        for file in os.listdir(absolute_path):
            if _file_is_yaml(file):
                configs += _load_config(os.path.join(absolute_path, file))
    for config in configs:
        app.config[CALL_COUNT_PARAM][config['id']] = 0
    app.config[CONFIG_PARAM] = configs
    return configs


def _file_is_yaml(file):
    return file.endswith(".yaml") or file.endswith(".yml")


def _validate_path(path):
    if os.path.isabs(path):
        response = path
    else:
        response = os.path.join(os.getcwd(), path)
    if not os.path.exists(response):
        raise Exception("Directory or File not found!")
    return response


def _load_config(file):
    with open(file, 'r') as stream:
        try:
            config, error = ConfigSchema(many=True).load(yaml.load(stream))
            if error:
                raise RuntimeError(error)
            return config
        except yaml.YAMLError as exc:
            raise RuntimeError(exc)
