import glob
import importlib
import json
import os
from typing import List

import yaml


def parse_conf(path: str) -> dict:
    if not (path.endswith('.json') or path.endswith('.yaml')):
        path = f'{path}.*'
    file_path = glob.glob(path)
    if len(file_path) != 1:
        raise RuntimeError(f'It is impossible to uniquely identify the file {file_path}')
    file_path = file_path[0]

    if file_path.endswith('.json'):
        with open(file_path) as f:
            return json.load(f)

    if file_path.endswith('.yaml'):
        with open(file_path) as f:
            return yaml.load(f, Loader=yaml.FullLoader)

    raise RuntimeError('Unknown format for config file. Only JSON and YAML supported')


def import_module(loader: str):
    module = loader[:loader.rfind('.')]
    func_name = loader.split('.')[-1]
    module = importlib.import_module(module)
    if not hasattr(module, func_name):
        raise RuntimeError(f'{func_name} is not found in {module}')
    return getattr(module, func_name)


def resolve_paths(sdl_paths: List) -> List:
    res = []

    for sdl_path in sdl_paths:
        if os.path.isfile(sdl_path):
            res.append(sdl_path)
        else:
            for path, dirs, files in os.walk(sdl_path):
                for file in files:
                    res.append(f'{path}/{file}')
    return res
