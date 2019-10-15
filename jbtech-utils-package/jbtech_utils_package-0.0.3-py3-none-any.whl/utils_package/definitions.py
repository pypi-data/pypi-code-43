import os
import json
from configparser import ConfigParser

PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
LIB_DIR = os.path.join(PACKAGE_DIR, 'data_controller/json_libraries')

CONFIG_PARSER = ConfigParser()
