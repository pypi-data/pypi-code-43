import os
import json

def load_config():
    config_path = None
    try:
        config_path = os.environ['MODELS_CONFIG']
    except KeyError:
        config_path = "config/database.json"

    with open(config_path) as cred_file:
        return json.loads(cred_file.read())
