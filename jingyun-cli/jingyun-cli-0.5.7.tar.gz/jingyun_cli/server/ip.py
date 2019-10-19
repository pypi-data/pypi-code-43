#! /usr/bin/env python
# coding: utf-8

from jingyun_cli import logger
from jingyun_cli.util.host import get_default_ip
from jingyun_cli.util.cli_args import args_man
from help import g_help

__author__ = '鹛桑够'


def get_ip():

    default_ip = get_default_ip()
    logger.info(default_ip)

if __name__ == "__main__":
    get_ip()
