#! /usr/bin/env python
# coding: utf-8

import sys
import os
import argparse
try:
    from .help import g_help, error_and_exit, jy_input
except ValueError:
    from help import g_help, error_and_exit, jy_input
from jingyun_cli.jingd import request_jingd


def request_sample(method, url, data):
    return request_jingd("sample", method, url, data)


def req_process():
    url = "/sample/process/"
    r_data = request_sample("GET", url, None)
    all_process = r_data["data"]
    return all_process


def req_process_detail(process_no):
    url = "/sample/process/detail/"
    r_data = request_sample("POST", url, dict(process_no=process_no))
    params = r_data["data"]["params"]
    return params


def req_sample_info(sample_no):
    url = "/sample/info/"
    r_data = request_sample("GET", url, dict(sample_no=sample_no))
    seq_files = r_data["data"]["seq_files"]
    return seq_files


def req_sample_right(sample_no):
    url = "/sample/right/"
    r_data = request_sample("GET", url, dict(sample_no=sample_no))
    rights = r_data["data"]
    return rights


def req_analysis(account, sample_no, seq_files, bucket, process_no):
    url = "/sample/analysis/v2/"
    data = dict(sample_no=sample_no, seq_files=seq_files, bucket=bucket, process_no=process_no, account=account)
    print(data)
    confirm = jy_input("Confirm?").lower()
    if confirm in ["y", "yes"]:
        r_data = request_sample("POST", url, data)


def re_run(sample_no, account=None):
    seq_files = req_sample_info(sample_no)
    if seq_files is None:
        error_and_exit("Not Found seq_files")
    files = seq_files.split(",")
    if account is None:
        rights = req_sample_right(sample_no)
        for item in rights:
            if item["role"] == 0:
                account = item["account"]
    if account is None:
        error_and_exit("Auto Find Account Fail, Please Set Account")
    process_no = -1
    all_process = req_process()
    for p in all_process:
        if p["process_name"] == files[0]:
            process_no = p["process_no"]
    if process_no == -1:
        error_and_exit("Not Found Process Name Is %s" % files[0])
    params = req_process_detail(process_no)
    r_seq_files = dict()
    for p in params:
        r_seq_files[p["param_name"]] = ""
    keys = r_seq_files.keys()
    if len(keys) != len(files) - 1:
        print(keys)
        print(files)
        error_and_exit("Please Check input file")
    bucket = None
    for i in range(len(keys)):
        bucket, file_path = files[i + 1].split(":", 1)
        r_seq_files[keys[i]] = file_path
    req_analysis(account, sample_no, r_seq_files, bucket, process_no)


def cli_main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--account", dest="account", help=g_help("user"))
    parser.add_argument("sample_no", help=g_help("sample_no"))
    if len(sys.argv) <= 1:
        sys.argv.append("-h")

    args = parser.parse_args()
    sample_no = int(args.sample_no)
    re_run(sample_no, args.account)


if __name__ == "__main__":
    sys.argv.extend(["205"])
    cli_main()
