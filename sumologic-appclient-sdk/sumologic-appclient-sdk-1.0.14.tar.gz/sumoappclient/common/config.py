# -*- coding: future_fstrings -*-
import os
import re

from common.logger import get_logger
from common.utils import merge_dict
import yaml


class Config(object):
    SUMO_CONFIG_FOLDER = "sumo"

    def __init__(self, logger=None):
        self.log = get_logger(__name__) if logger is None else logger

    def get_config(self, config_filename, root_dir, input_cfgpath=''):
        ''' reads base config and merges with user config'''
        base_config_path = os.path.join(root_dir, config_filename)
        base_config = self.read_config(base_config_path)

        cfg_locations = self.get_config_locations(input_cfgpath, config_filename)
        usercfg = self.get_user_config(cfg_locations)
        if not usercfg:
            usercfg = self.get_config_from_env(base_config)
        self.log.info(f'''usercfg: {usercfg.keys()}''')
        self.config = merge_dict(base_config, usercfg)
        self.validate_config(self.config)
        self.log.info(f"config object created")
        return self.config

    def convert_if_digit(self, val):
        if isinstance(val, (str, bytes)):
            try:
                num = int(val)
            except ValueError:
                try:
                    num = float(val)
                except ValueError:
                    num = val
        else:
            num = val
        return num

    def validate_config(self, config):
        has_all_params = True
        for section, section_cfg in config.items():
            if not section_cfg:
                raise Exception(f'''{section_cfg} is empty in config: {self.user_config_path}''')
            for k, v in section_cfg.items():
                if v is None:
                    self.log.error(f"Missing parameter {k} from config")
                    has_all_params = False
                elif "endpoint" in k.lower():
                    self.is_valid_url(v)
                else:
                    section_cfg[k] = self.convert_if_digit(v)

        if not has_all_params:
            raise Exception("Invalid config")

    def is_valid_url(self, url):
        regex = re.compile(
            r'^(?:http|ftp)s?://'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        if re.match(regex, url) is None:
            self.log.warning(f"{url} does not match valid url regex")

    def get_config_from_env(self, base_config):
        self.log.info("fetching parameters from environment")
        cfg = {}
        for section, section_cfg in base_config.items():
            new_section_cfg = {}
            for k, v in section_cfg.items():
                if k in os.environ:
                    new_section_cfg[k] = os.environ[k]
                else:
                    new_section_cfg[k] = v
            cfg[section] = new_section_cfg
        return cfg

    def get_config_locations(self, input_cfgpath, config_filename):
        home_dir = os.path.expanduser("~")
        hom_dir_path = os.path.join(home_dir, config_filename)
        sumo_dir_path = os.path.join(home_dir, self.SUMO_CONFIG_FOLDER, config_filename)
        cfg_locations = [input_cfgpath, sumo_dir_path, hom_dir_path, os.getenv("SUMO_API_COLLECTOR_CONF", '')]
        return filter(lambda p: os.path.isfile(p), cfg_locations)

    def get_user_config(self, cfg_locations):
        usercfg = {}
        for filepath in cfg_locations:
            if os.path.isfile(filepath):
                usercfg = self.read_config(filepath)
                self.user_config_path = filepath
                break
        return usercfg

    def read_config(self, filepath):
        self.log.info(f"Reading config file: {filepath}")
        config = {}
        with open(filepath, 'r') as stream:
            try:
                config = yaml.load(stream)
            except yaml.YAMLError as exc:
                self.log.error(f"Unable to read config {filepath} Error: {exc}")
                raise
        return config
