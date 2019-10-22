import configparser

from whatcha_readin.paths import WhatchaReadinPaths

VERSION = "0.0.2"


def get_config():
    config_path = WhatchaReadinPaths.get_config_path()
    config = configparser.ConfigParser()
    config.read(config_path)
    return config
