import json
import os


def get_configs(config_file):
    if os.path.exists(config_file):
        return json.loads(open(config_file).read())
    else:
        raise FileNotFoundError(
            "Please path get_configs a full path to the config file"
        )
