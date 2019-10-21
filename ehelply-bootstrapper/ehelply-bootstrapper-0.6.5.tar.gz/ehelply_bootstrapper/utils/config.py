from typing import List


def load_config(config_path, configs: List[str] = None):
    from ehelply_bootstrapper.utils.state import State
    from pymlconf import Root

    State.config = Root()
    State.config.load_file(config_path + '/bootstrap.yaml')
    State.config.load_file(config_path + '/app.yaml')

    if configs:
        for config in configs:
            State.config.load_file(config_path + '/' + config)
