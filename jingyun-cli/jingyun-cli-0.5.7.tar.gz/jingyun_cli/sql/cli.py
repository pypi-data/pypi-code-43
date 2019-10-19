#! /usr/bin/env python
# coding: utf-8

import os
import sys
import re
from mysqldb_rich.db2 import TableDB, DB
from jingyun_cli import logger
from jingyun_cli.util.cli_args import args_man
from jingyun_cli.util.help import error_and_exit
from jingyun_cli.util.env import get_environ
try:
    from .help import g_help
except ValueError:
    from help import g_help

__author__ = '鹛桑够'


def check_file_exist(file_path):
    if os.path.exists(file_path) is False:
        error_and_exit(g_help("file_lost", file_path))


def create_table(args):
    if args.conf_path is None:
        args.conf_path = get_environ("DB_CONF_PATH")
    t = TableDB(conf_path=args.conf_path)
    suffix_comp = re.compile(r"\w+\.(json|function|procedure|trigger|view)$", re.I)
    all_files = args.files
    if args.file_prefix is not None:
        all_files = map(lambda x: args.file_prefix + x, all_files)
    if args.directory is not None:
        desc_files = os.listdir(args.directory)
        all_files.extend(map(lambda x: os.path.join(args.directory, x), desc_files))
    for file_path in all_files:
        filename = os.path.split(file_path)[1]
        if suffix_comp.match(filename) is None:
            logger.warning(g_help("skip_file", file_path))
            continue
        logger.info(g_help("handle_file", file_path))
        check_file_exist(file_path)
        if file_path.endswith(".json"):
            r = t.create_from_json_file(file_path)
        else:
            with open(file_path) as rf:
                c = rf.read()
                ds = re.findall(r"(DROP[\s\S]+? IF EXISTS[\s\S]+?(;|\n))", c, re.I)
                for item in ds:
                    t.execute(item[0])
                fs = re.findall(r"(CREATE[\s\S]+?(END;|END\n|$))", c)
                for item in fs:
                    t.execute(item[0])


def op_table():
    commands_man = args_man.add_subparsers(title="Commands", description=None, metavar="COMMAND OPTIONS", dest="sub_cmd")
    create_man = commands_man.add_parser("create", help=g_help("create"))
    create_man.add_argument("-c", metavar="path", dest="conf_path", help=g_help("conf_path"))
    create_man.add_argument("-d", metavar="path", dest="directory", help=g_help("dir"))
    create_man.add_argument("--file-prefix", metavar="path", dest="file_prefix", help=g_help("file_prefix"))
    create_man.add_argument("-f", metavar="path", dest="files", help=g_help("file"), nargs="*", default=[])

    if len(sys.argv) <= 1:
        sys.argv.append("-h")
    args = args_man.parse_args()
    if args.sub_cmd == "create":
        create_table(args)


def link():
    args_man.add_argument("-c", metavar="path", dest="conf_path", help=g_help("conf_path"))
    args_man.add_argument("-r", "--readonly", dest="readonly", action="store_true", help=g_help("readonly"),
                          default=False)
    args = args_man.parse_args()
    if args.conf_path is None:
        args.conf_path = get_environ("DB_CONF_PATH")
    t = DB(conf_path=args.conf_path, readonly=args.readonly)
    t.link()

if __name__ == "__main__":
    # sys.argv.extend(["create", "-h"])
    # sys.argv.extend(["create", "-c", "/mnt/dataJINGD/conf/mysql_app.conf", "-d", "../../../GATCAPI/Table/Function/", "--file-prefix", "../../../GATCAPI/Table/Trigger/", "-f", "t_update_stage.trigger", "t_update_stage.trigger"])
    sys.argv.extend(["-c", "/mnt/data/JINGD/conf/mysql_app.conf"])
    link()
