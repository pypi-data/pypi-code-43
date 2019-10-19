#! /usr/bin/env python
# coding: utf-8

import os
import sys
import argparse
from supervisor.supervisorctl import main as supervisorctl_main
from supervisor.supervisord import main as supervisord_main
from jingyun_cli import logger

try:
    from .help import g_help, error_and_exit
except ValueError:
    from help import g_help, error_and_exit

__author__ = '鹛桑够'


