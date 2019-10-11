#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   command.py
@Time    :   2019/10/11 15:09:47
@Author  :   lateautumn4lin
@PythonVersion  :   3.7
'''

import argparse
from .core.initialize import Initialize
from .logger import logger

parser = argparse.ArgumentParser(
    description='Auto Create Robust Web Projects Of Python3 For Humans'
)
parser.add_argument(
    "-N",
    "--name",
    default="test",
    help='Customize Project Name'
)
args = parser.parse_args()


def main():
    init = Initialize()
    init.create(
        project_name=args.name,
    )


main()
