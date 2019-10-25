import jsonpickle
from telegram_bot_sdk import config

_PATH_TO_CONFIG = "res/config.json"


def load_config(path=_PATH_TO_CONFIG):
    print("load config")
    try:
        with open(path) as f:
            return jsonpickle.decode(f.read())
    except FileNotFoundError:
        print("Config file was not found")
        return create_init_config()


def save_config(config_object, path=_PATH_TO_CONFIG):
    try:
        with open(path, 'w') as f:
            f.write(jsonpickle.encode(config_object))
    except IOError:
        print("Config file could not be written to")


def create_init_config():
    print("Creating new config")
    cfg = config.Config()
    cfg.vars["URL"] = "https://api.telegram.org/botYOUR-BOT-TOKEN-HERE/"
    save_config(cfg)
    return cfg
