# Python modules
from __future__ import division

# 3rd party modules

# Our modules
import vespa.common.util.config as util_config

def get_window_coordinates(window_name):
    """A shortcut for the Config object method of the same name."""
    config = Config()
    return config.get_window_coordinates(window_name)


class Config(util_config.BaseConfig):
    def __init__(self):
        util_config.BaseConfig.__init__(self, "pulse.ini")
