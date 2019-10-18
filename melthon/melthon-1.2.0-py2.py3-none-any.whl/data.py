from pathlib import Path

import yaml


def get_yml_data(path):
    data = {}
    for filename in Path(path).glob('*.yml'):
        with filename.open(mode='r') as file_config:
            data[filename.stem] = yaml.safe_load(file_config)
    return data
