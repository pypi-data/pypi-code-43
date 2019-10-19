import sys
import re
import argparse


_PAT_WHITESPACE = re.compile(r'\s')



def parse_arg_file(p):
    with open(p, 'r') as f:
        args = {}
        section_delimiter = None
        for l in f:
            if not l.strip():  # empty line
                continue
            if not _PAT_WHITESPACE.match(l):  # new section delimiter
                section_delimiter = l.strip()
                args[section_delimiter] = []
            else:
                assert section_delimiter
                args[section_delimiter].extend(l.strip().split())
        if 'all' not in args.keys():
            raise ValueError('Expected "all" section, got {}'.format(args.keys()))
        return args


def get_args(ps):
    command_line_args = sys.argv[1:]
    file_args = {}
    for p in ps:
        file_args.update(parse_arg_file(p))

    args = file_args['all']
    section = _get_section(file_args, command_line_args)
    if section:
        args += file_args[section]
    args += command_line_args

    return args


def _get_section(file_args, command_line_args):
    for section in file_args.keys():
        if section == 'all':
            continue
        if section in command_line_args:
            return section
    return None


from pprint import pprint
pprint(get_args(['runconfig']))


