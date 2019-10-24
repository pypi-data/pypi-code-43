import os, json

def read_params():
    if os.path.isfile("/etc/safer/params.json"):
        return read_config("/etc/safer/params.json")
    return read_config("./params.json")

def read_config(config_file):
    with open(config_file, 'r') as f:
        config = json.load(f)
    return config

