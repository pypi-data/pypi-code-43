# !/usr/bin/python
# -*- coding: UTF-8 -*-
"""
Created on MAY 21, 2018
@author: zlh
"""
import yaml


def read_from_yaml(file: str) -> dict:
    with open(file) as f:
        conf_dic = yaml.load(f.read(),
                             Loader=yaml.FullLoader)
    return conf_dic


def get_config_str(file: str, key: str) -> str:
    conf_dic = read_from_yaml(file)
    return conf_dic.get(key, "")


def get_config_int(file: str, key: str) -> int:
    conf_dic = read_from_yaml(file)
    return conf_dic.get(key, 0)


if __name__ == "__main__":
    print(read_from_yaml("config/dev/server_config.yaml"))
