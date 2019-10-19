#! /usr/bin/env python
# coding: utf-8

import os
import subprocess

__author__ = '鹛桑够'


loaded_profile = set()


def source(filename):
    if os.path.exists(filename) is False:
        return
    abs_filename = os.path.abspath(filename)
    if abs_filename in loaded_profile:
        return
    cmd = "source %s && env" % filename
    output = subprocess.check_output(cmd, shell=True)
    lines = output.split("\n")
    for line in lines:
        if len(line) <= 0:
            continue
        key_value = line.split("=", 1)
        if len(key_value) != 2:
            continue
        key, value = key_value
        os.environ[key] = value


def source_local():
    home_dir = os.environ.get("HOME")
    local_profile = os.path.join(home_dir, ".bash_profile")
    source(local_profile)


def get_environ(key, failobj=None):
    source_local()
    return os.environ.get(key, failobj)


if __name__ == "__main__":
    MYSQL_ROOT_DIR = os.environ.get("MYSQL_ROOT_DIR")
    print(MYSQL_ROOT_DIR)
    source_local()
    MYSQL_ROOT_DIR = os.environ.get("MYSQL_ROOT_DIR")
    print(MYSQL_ROOT_DIR)