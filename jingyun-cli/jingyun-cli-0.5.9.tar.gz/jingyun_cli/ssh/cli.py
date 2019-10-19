#! /usr/bin/env python
# coding: utf-8

import os
import sys
import argparse
import requests
import datetime
import re
from jingyun_cli import logger

try:
    from .help import g_help, error_and_exit
except ValueError:
    from help import g_help, error_and_exit

__author__ = '鹛桑够'


arg_man = argparse.ArgumentParser()
default_endpoint = "http://jy-softs.oss-cn-beijing.aliyuncs.com"


def download_ssh_key(endpoint, oss_file, *oss_dir):
    endpoint = endpoint.rstrip("/")
    oss_dirs = map(lambda x: x.strip("/"), oss_dir)
    oss_dirs = filter(lambda x: x != "", oss_dirs)
    dir_path = "/".join(oss_dirs)
    if len(dir_path) > 0:
        url = "%s/%s/%s" % (endpoint, dir_path, oss_file)
    else:
        url = "%s/%s" % (endpoint, oss_file)
    resp = requests.get(url)
    return resp.status_code, resp.text


def write_file(save_dir, filename, content):
    save_path = os.path.join(save_dir, filename)
    if os.path.exists(save_path) is True:
        logger.debug("%s exist" % filename)
        with open(save_path, "r") as r:
            old_content = r.read()
            if old_content == content:
                logger.debug("%s old content is right" % filename)
                os.system("chmod 600 %s" % save_path)
                return save_path
            back_name = filename + ".jy" + datetime.datetime.now().strftime("%y%m%d%H%M") + ".bk"
            back_path = os.path.join(save_dir, back_name)
            logger.debug("backup old %s to %s" % (filename, back_name))
            with open(back_path, "w") as w:
                w.write(old_content)
    with open(save_path, "w") as w:
        w.write(content)
    os.system("chmod 600 %s" % save_path)
    return save_path


def write_authorized_keys(ssh_dir, content):
    save_path = os.path.join(ssh_dir, "authorized_keys")
    if os.path.exists(save_path) is True:
        with open(save_path, "r") as r:
            all_lines = r.readlines()
            if content in all_lines:
                os.system("chmod 600 %s" % save_path)
                return True
    with open(save_path, "a") as w:
        w.write(content)
    os.system("chmod 600 %s" % save_path)
    return True


def gen_key():
    cmd = ["ssh-keygen", "-C", "meisanggou", "-f", "id_rsa", "-N", "''"]


def non_key():
    arg_man.add_argument("-d", "--oss-dir", dest="oss_dir", help=g_help("oss_dir"), metavar="", default="ssh-key")
    arg_man.add_argument("-e", "--endpoint", dest="endpoint", help=g_help("endpoint"), metavar="",
                         default=default_endpoint)
    save_dir = os.path.join(os.environ.get("HOME"), ".ssh")
    os.system("mkdir -p %s" % save_dir)
    os.system("chmod 700 %s" % save_dir)
    jingd_env = os.environ.get("JINGD_ENV", "")

    args = arg_man.parse_args()
    code, content = download_ssh_key(args.endpoint, "id_rsa", args.oss_dir, jingd_env)
    code_pub, content_pub = download_ssh_key(args.endpoint, "id_rsa.pub", args.oss_dir, jingd_env)
    if code != 200 or code_pub != 200:
        if jingd_env == "":
            msg = "id_rsa: %s\nid_ras.pub: %s" % (code, code_pub)
            error_and_exit(msg)
        code, content = download_ssh_key(args.endpoint, "id_rsa", args.oss_dir)
        code_pub, content_pub = download_ssh_key(args.endpoint, "id_rsa.pub", args.oss_dir)
        if code != 200 or code_pub != 200:
            msg = "id_rsa: %s\nid_ras.pub: %s" % (code, code_pub)
            error_and_exit(msg)
    write_file(save_dir, "id_rsa", content)
    write_file(save_dir, "id_rsa.pub", content_pub)
    write_authorized_keys(save_dir, content_pub)


if __name__ == "__main__":

    non_key()
