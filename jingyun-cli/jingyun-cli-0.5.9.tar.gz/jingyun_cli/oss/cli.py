#! /usr/bin/env python
# coding: utf-8

import os
import sys
import requests
from jingyun_cli import logger
from jingyun_cli.util.cli_args import args_man
from jingyun_cli.util.env import get_environ
try:
    from .help import g_help, error_and_exit
except ValueError:
    from help import g_help, error_and_exit

__author__ = '鹛桑够'


default_endpoint = "http://jy-softs.oss-cn-beijing.aliyuncs.com"


def head_url(url):
    resp = requests.head(url)
    return resp.status_code


def add_output():
    args_man.add_argument("-o", "--output", dest="output", help=g_help("output"), metavar="output")


def get_download_url(endpoint, oss_file, *oss_dir):
    endpoint = endpoint.rstrip("/")
    oss_dirs = map(lambda x: x.strip("/"), oss_dir)
    oss_dirs = filter(lambda x: x != "", oss_dirs)
    dir_path = "/".join(oss_dirs)
    if len(dir_path) > 0:
        url = "%s/%s/%s" % (endpoint, dir_path, oss_file)
    else:
        url = "%s/%s" % (endpoint, oss_file)
    return url


def download_action(endpoint, oss_dir, oss_item, save_path, force=False, custom_dir=""):
    if os.path.exists(save_path) is True and force is False:
        logger.warning(g_help("exist", oss_item))
        return 0
    logger.info(g_help("download", oss_item, save_path))
    custom_url = ""
    if custom_dir != "":
        custom_url = get_download_url(endpoint, oss_item, oss_dir, custom_dir)
        code = head_url(custom_url)
        if code != 200:
            logger.debug(g_help("head_error", custom_url, code))
            custom_url = ""
    if custom_url == "":
        url = get_download_url(endpoint, oss_item, oss_dir)
        code = head_url(url)
        if code != 200:
            error_and_exit(g_help("head_error", url, code))
    else:
        url = custom_url
    cmd = ["curl", "-o", save_path, url]
    e_code = os.system(" ".join(cmd))
    return e_code


def multi_download():
    args_man.add_argument("--allow-custom", dest="allow_custom", help=g_help("allow_custom"), action="store_true", default=False)
    args_man.add_argument("-d", "--oss-dir", dest="oss_dir", help=g_help("oss_dir"), metavar="", default="")
    args_man.add_argument("-e", "--endpoint", dest="endpoint", help=g_help("endpoint"), metavar="",
                         default=default_endpoint)
    args_man.add_argument("-n", "--name", dest="name", metavar="filename", help=g_help("name"))
    args_man.add_argument("-f", "--force", action="store_true", help=g_help("force"), default=False)
    args_man.add_argument("files", metavar="oss_file", nargs="*", help=g_help("oss_file"))
    add_output()
    if len(sys.argv) <= 1:
        sys.argv.append("-h")
    args = args_man.parse_args()
    allow_custom = args.allow_custom
    if allow_custom is True:
        jingd_env = get_environ("JINGD_ENV", "")
        if jingd_env == "":
            logger.warning(g_help("empty_env"))
    else:
        jingd_env = ""
    f_inputs = args.files
    out_dir = args.output
    if out_dir is None:
        out_dir = "."
    if len(f_inputs) == 1:
        name = args.name if args.name is not None else f_inputs[0]
        save_path = os.path.join(out_dir, name)
        e_code = download_action(args.endpoint, args.oss_dir, f_inputs[0], save_path, force=args.force)
        if e_code != 0:
            error_and_exit(g_help("error", f_inputs[0]))
    else:
        for item in f_inputs:
            save_path = os.path.join(out_dir, item)
            e_code = download_action(args.endpoint, args.oss_dir, item, save_path, force=args.force, custom_dir=jingd_env)
            if e_code != 0:
                error_and_exit(g_help("error", item))

if __name__ == "__main__":
    sys.argv.extend(["-d", "shell", "nonkey.sh", "deploy_api.sh", "-n", "a.sh", "-f", "--allow-custom", "--debug"])
    multi_download()
