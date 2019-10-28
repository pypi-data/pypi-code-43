#!/usr/bin/python
import argparse

from commands import LoadConfigCommand
from receivers import LoadConfig
from commands import GetConfigCommand
from receivers import GetConfig
from commands import TableUpdateCommand
from receivers import TableUpdate
from commands import TableDumpCommand
from receivers import TableDump
from client import P4RuntimeClient
from lib import P4InfoHelper


def do_load_config(args):
    load_config = LoadConfig(P4RuntimeClient(), args)
    command = LoadConfigCommand(load_config)
    command.execute()


def do_get_config(args):
    get_config = GetConfig(P4RuntimeClient(), args)
    command = GetConfigCommand(get_config)
    p4info_status = command.execute()

    if args.show and p4info_status:
        p4info = P4InfoHelper.read_from_file(args.p4info_file_path)
        print "P4 Info: "
        print p4info


def do_table_update(args):
    table_update = TableUpdate(P4RuntimeClient(), args)
    command = TableUpdateCommand(table_update)
    command.execute()


def do_table_delete():
    pass


def do_table_dump(args):
    table_dump = TableDump(P4RuntimeClient(), args)
    command = TableDumpCommand(table_dump)
    command.execute()


def get_parser():
    parser = argparse.ArgumentParser(description='P4 runtime CLI')

    sp = parser.add_subparsers(dest='cmd')

    add_load_config_parser(sp)
    add_get_config_parser(sp)
    add_table_update_parser(sp)
    add_table_delete_parser(sp)
    add_table_dump_parser(sp)

    return parser


def add_load_config_parser(subparser):
    parser = subparser.add_parser('load_config')
    parser.add_argument('--pipeline-id', type=int, default=0, required=True)
    parser.add_argument('--p4info-path', type=str, default='/tmp/p4/basic.p4info', help='path to p4info file',
                        required=True)
    parser.add_argument('--config-path', type=str, default='/tmp/p4/basic.json', help='path to device config file',
                        required=True)


def add_get_config_parser(subparser):
    parser = subparser.add_parser('get_config')
    parser.add_argument('--pipeline-id', type=int, default=0, required=True)
    parser.add_argument('--response-type', choices=['ALL', 'P4INFO_AND_COOKIE', 'DEVICE_CONFIG_AND_COOKIE'],
                        default='ALL')
    parser.add_argument('--show', action='store_true', help='shows a p4info file on this console')
    parser.add_argument('--p4info-path', type=str, default='/tmp/p4/save.p4info',
                        help='path where p4info file retrieved from a device will be stored', required=True)
    parser.add_argument('--config-path', type=str, default='/tmp/p4/save.json',
                        help='path where config file retrieved from a device will be stored', required=True)


def add_table_update_parser(subparser):
    parser = subparser.add_parser('table_update')
    parser.add_argument('--pipeline-id', type=int, default=0, required=True)
    parser.add_argument('--p4info-path', type=str, default='/tmp/p4/save.p4info',
                        help='path where p4info file retrieved from a device will be stored', required=True)
    parser.add_argument('--entry', nargs='+', help='<table> <key1=value> <key2=value> ... <action=param1,param2,...>', required=True)


def add_table_delete_parser(subparser):
    parser = subparser.add_parser('table_delete')


def add_table_dump_parser(subparser):
    parser = subparser.add_parser('table_dump')
    parser.add_argument('--pipeline-id', type=int, default=0, required=True)
    parser.add_argument('--p4info-path', type=str, default='/tmp/p4/save.p4info',
                        help='path where p4info file retrieved from a device will be stored', required=True)
    parser.add_argument('--table', type=str, help='Table name', required=True)


def main():
    parser = get_parser()
    args = parser.parse_args()

    options = {
        'load_config': do_load_config,
        'get_config': do_get_config,
        'table_update': do_table_update,
        'table_delete': do_table_delete,
        'table_dump': do_table_dump
    }

    func = options[args.cmd]
    func(args)


if __name__ == '__main__':
    main()
