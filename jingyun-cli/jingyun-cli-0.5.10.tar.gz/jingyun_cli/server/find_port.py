#! /usr/bin/env python
# coding: utf-8

import sys
import re
from jingyun_cli import logger
from jingyun_cli.util.port import is_listen
from jingyun_cli.util.cli_args import args_man
from help import g_help

__author__ = '鹛桑够'


redis = [6379, 9532, 9531, 9530, 9529, 9528, 9527, 9526, 9525, 9524,
         6379, 8532, 8531, 8530]
mysql = [3306, 9536, 9537, 9538, 9539, 9540, 9541, 9542, 9543, 9544,
         3306, 8536, 8537, 8538]
nginx = [80, 9580, 9579, 9579, 9578]
registry = [5000, 5001, 5002, 5003, 5004, 5005, 5006, 5007, 5008, 5009,
            5010]

define_server = dict(nginx=nginx, mysql=mysql, redis=redis, registry=registry)


def find_one_port():
    args_man.add_argument("-s", "--server", dest="server", help=g_help("server"), choices=define_server.keys())
    args_man.add_argument("-p", "--ports", dest="ports", help=g_help("port"), nargs="*")

    args = args_man.parse_args()
    all_ports = []
    if args.server is not None:
        all_ports.extend(define_server[args.server])
    if args.ports is not None:
        for port in args.ports:
            ports = re.split(r"\D", port)
            ports = map(lambda x: int(x), filter(lambda x: len(x) > 0, ports))
            all_ports.extend(ports)
    for item in all_ports:
        logger.debug("check is listen %s" % item)
        if is_listen(item) is False:
            logger.info(item)
            sys.exit(0)
    sys.exit(1)

if __name__ == "__main__":
    sys.argv.extend(["-p", "9532", "80,2201,,2200"])
    find_one_port()