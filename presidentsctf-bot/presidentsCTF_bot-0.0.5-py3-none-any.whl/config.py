#!/usr/bin/env python3

"""
Config - allow loading a configuration file from the local directory, or use
the provided sane defaults.
"""

import json
import os.path
import logging

default_path = "config.json"

# default values
config = {"db": "presidents_cup.sqlite3",
          "events":[],
          "teams": {},                      # optional mapping to known names
          "slack":{},                       # optional slack app credentials
          "twitter":{}                      # optional twitter app credentials
          }

def load_config(path=default_path):
    global config
    if os.path.isfile(path):
        logging.debug("Loading config from: {}".format(path))
        with open(path) as inf:
            config = json.loads(inf.read())
    else:
        logging.debug("Using default config")
