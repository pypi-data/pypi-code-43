#! /usr/bin/env python
# coding: utf-8

import os
import sys
import argparse
import json
try:
    from .help import g_help, error_and_exit
except ValueError:
    from help import g_help, error_and_exit

__author__ = '鹛桑够'


arg_man = argparse.ArgumentParser()


def add_output():
    arg_man.add_argument("-o", "--output", dest="output", help=g_help("output"), metavar="out")


def load_json(file_path):
    if os.path.exists(file_path) is False:
        msg = g_help("file_not_exist", file_path)
        error_and_exit(msg)
    try:
        with open(file_path) as rf:
            c = rf.read()
    except IOError:
        error_and_exit(g_help("read_error", file_path))
        return
    try:
        o = json.loads(c)
        return o
    except ValueError:
        error_and_exit(g_help("content_error", file_path))
        return


def json_output(o, file_path=None):
    o_s = json.dumps(o, indent=2)
    if file_path is not None:
        with open(file_path, "w") as wf:
            wf.write(o_s)
    else:
        print(o_s)


def json_merge():
    arg_man.add_argument("-i", "-I", "--input", dest="input", help=g_help("json_file"), action="append",
                         metavar="json_file", default=[])
    arg_man.add_argument("inputs", metavar="json_file", nargs="*", help=g_help("json_file"))
    add_output()
    if len(sys.argv) <= 1:
        sys.argv.append("-h")
    args = arg_man.parse_args()
    f_inputs = args.inputs
    f_inputs.extend(args.input)
    o = dict()
    for f in f_inputs:
        f_o = load_json(f)
        o.update(f_o)
    json_output(o, args.output)


def json_update():
    arg_man.add_argument("-c", "-C", dest="cover", help=g_help("cover"), action="store_true", default=False)
    arg_man.add_argument("-i", "-I", "--input", dest="input", help=g_help("json_file"), metavar="json_file")
    arg_man.add_argument("inputs", metavar="json_file", nargs="?", help=g_help("json_file"))
    add_output()
    if len(sys.argv) <= 1:
        sys.argv.append("-h")

    args = arg_man.parse_args()
    o = load_json(args.input)
    pass


def main():
    pass


if __name__ == "__main__":
    # sys.argv.append("a.json")
    # sys.argv.extend(["-i", "b.json"])
    # sys.argv.extend(["-o", "b.json"])

    json_update()