#! /usr/bin/env python
# coding: utf-8

import sys
import os
import requests
import argparse
try:
    from .help import g_help, error_and_exit
except ValueError:
    from help import g_help, error_and_exit

user_agent = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"


def request_auth(method, url, data):
    auth_endpoint = os.environ.get("JINGD_AUTH_ENDPOINT")
    if auth_endpoint is None:
        error_and_exit(g_help("defect_env", "JINGD_AUTH_ENDPOINT"), -1)
    headers = {"Content-Type": "application/json", "User-Agent": user_agent}
    url = "%s%s" % (auth_endpoint, url)
    resp = requests.request(method, url, headers=headers, json=data)
    if resp.status_code != 200:
        error_and_exit(resp.status_code)
    r_data = resp.json()
    if r_data["status"] % 10000 < 100:
        print(r_data["message"])
    else:
        error_and_exit(r_data["message"])


def request_api(method, url, data):
    api_endpoint = os.environ.get("JINGD_API_ENDPOINT")
    if api_endpoint is None:
        error_and_exit(g_help("defect_env", "JINGD_API_ENDPOINT"), -1)
    headers = {"Content-Type": "application/json", "User-Agent": user_agent}
    url = "%s%s" % (api_endpoint, url)
    resp = requests.request(method, url, headers=headers, json=data)
    if resp.status_code != 200:
        error_and_exit(resp.status_code)
    r_data = resp.json()
    if r_data["status"] % 10000 < 100:
        print(r_data["message"])
    else:
        error_and_exit(r_data["message"])


def new_user(account, password):
    url = "/auth/"
    method = "POST"
    data = {"account": account, "password": password}
    request_auth(method, url, data)


def reset_password(account, password):
    url = "/auth/password/reset/admin/"
    method = "PUT"
    data = {"account": account, "new_password": password}
    request_auth(method, url, data)


def block_user(account):
    url = "/auth/account/block/admin/"
    method = "PUT"
    data = {"account": account}
    request_auth(method, url, data)


def unlock_user(account):
    url = "/auth/account/unlock/admin/"
    method = "PUT"
    data = {"account": account}
    request_auth(method, url, data)


def grant_genetic(account):
    url = "/api/v2/auth/grant/genetic/"
    method = "POST"
    data = {"account": account, "auth_code": "JINGDu"}
    request_api(method, url, data)


def cli_main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--action", dest="action", help=g_help("action"), choices=["reset", "block", "unlock",
                                                                                         "genetic", "new"])
    parser.add_argument("-u", "--user", dest="user", help=g_help("user"))
    parser.add_argument("-p", "--password", dest="password", help=g_help("new_password"), default="123456")
    if len(sys.argv) <= 1:
        sys.argv.append("-h")

    args = parser.parse_args()

    if args.action is None:
        error_and_exit("Please Set [action] use -a or --action", 1)
    if args.user is None:
        error_and_exit("Please Set [user] use -u or --user", 2)
    if args.action == "reset":
        reset_password(args.user, args.password)
    elif args.action == "block":
        block_user(args.user)
    elif args.action == "unlock":
        unlock_user(args.user)
    elif args.action == "genetic":
        grant_genetic(args.user)
    elif args.action == "new":
        new_user(args.user, args.password)


if __name__ == "__main__":
    sys.argv.extend(["-a", "genetic", "-u", "zh_test"])
    cli_main()
