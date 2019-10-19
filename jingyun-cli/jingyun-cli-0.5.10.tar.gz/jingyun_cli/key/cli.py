#! /usr/bin/env python
# coding: utf-8

import os
import sys
import requests
import argparse
try:
    from .help import g_help, error_and_exit
except ValueError:
    from help import g_help, error_and_exit

__author__ = '鹛桑够'


default_endpoint = "https://dms.gene.ac/dist/key/"
headers = {"User-Agent": "jyrequests"}
arg_man = argparse.ArgumentParser()


def add_output():
    arg_man.add_argument("-o", "--output", dest="output", help=g_help("output"), metavar="output")


def get_key(endpoint, app, filters):
    params = dict(app=app)
    for item in filters:
        s = item.split("=", 1)
        if len(s) != 2:
            error_and_exit(g_help("error_filter", item))
        params[s[0]] = s[1]
    try:
        resp = requests.get(endpoint, params=params, headers=headers)
        if resp.status_code != 200:
            error_and_exit(g_help("error_get", resp.status_code))
        r_data = resp.json()
        if r_data["status"] is False:
            error_and_exit(r_data["data"])
        data = r_data["data"]
        for key in data.keys():
            if key[0] == "_":
                data[key[1:]] = data[key]
                del data[key]
    except requests.RequestException as re:
        error_and_exit(g_help("error_get", str(re)))
        return
    except ValueError as ve:
        error_and_exit(g_help("error_get", str(ve)))
        return
    except KeyError as ke:
        error_and_exit(g_help("error_get", str(ke)))
        return
    return data


def replace_file(file_path, value_dict):
    if file_path is None:
        return
    if os.path.exists(file_path) is False:
        msg = g_help("file_not_exist", file_path)
        error_and_exit(msg)
    try:
        with open(file_path) as rf:
            c = rf.read()
    except IOError:
        error_and_exit(g_help("read_error", file_path))
        return
    c2 = c % value_dict
    try:
        with open(file_path, "w") as wf:
            wf.write(c2)
    except IOError:
        error_and_exit(g_help("write_error", file_path))
        return


def handle_key():
    arg_man.add_argument("-a", "--app", dest="app", help=g_help("app"), metavar="app_name", default="")
    arg_man.add_argument("-e", "--endpoint", dest="endpoint", help=g_help("endpoint"), metavar="Endpoint",
                         default=default_endpoint)
    arg_man.add_argument("-f", "--filters", dest="filters", help=g_help("filters"), action="append", default=[])
    arg_man.add_argument("-p", "--print", dest="print_key", help=g_help("print_key"), nargs="*", metavar="key")
    arg_man.add_argument("--only-value", dest="only_value", help=g_help("only_value"), action="store_true",
                         default=False)
    arg_man.add_argument("-r", "--replace", dest="replace_file", help=g_help("replace_file"), metavar="file")
    if len(sys.argv) <= 1:
        sys.argv.append("-h")
    args = arg_man.parse_args()
    key_items = get_key(args.endpoint, args.app, args.filters)
    replace_file(args.replace_file, key_items)
    if args.print_key is not None:
        for p_key in args.print_key:
            if p_key in key_items:
                if args.only_value is True:
                    print(key_items[p_key])
                else:
                    print("%s\t%s" % (p_key, key_items[p_key]))
            else:
                error_and_exit(g_help("key_not_exist", p_key))

if __name__ == "__main__":
    sys.argv.extend(["-a", "mns", "-r", "mns.conf", "-p", "region", "access_id", "-f", "ljd=true", "--only-value"])
    handle_key()
