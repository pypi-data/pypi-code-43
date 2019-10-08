import json
import os
from .git import get_repo_dir

def parse_conf_file(path):
    return json.loads(open(path).read())

def get_default_conf():
    return {
        "record_dir": None, # Record directory path relative to repo root
        "editor": "vim",
        "auto_add": True,
        "default_comparison_base": "master",
        "postgrator_dir": None,
    }

def get_conf_paths():
    paths = []
    
    repo_dir = get_repo_dir()
    if repo_dir is not None:
        repo_conf_path = os.path.join(get_repo_dir(), '.brailconf')
        if os.path.exists(repo_conf_path):
            paths.append(repo_conf_path)

    home_conf_path = os.path.join(os.path.expanduser("~"), '.brailconf')
    if os.path.exists(home_conf_path):
        paths.append(home_conf_path)
    
    return paths

def merge_confs(confs):
    merged_conf = get_default_conf()
    for conf in confs:
        merged_conf = {**merged_conf, **conf}
    return merged_conf