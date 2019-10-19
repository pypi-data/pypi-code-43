#! /usr/bin/env python
# coding: utf-8

import os
import requests
try:
    from .help import g_help, error_and_exit
except ValueError:
    from help import g_help, error_and_exit

__author__ = '鹛桑够'


user_agent = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"


def request_jingd(service, method, url, data):
    endpoint_env = "JINGD_%s_ENDPOINT" % service.upper()
    auth_endpoint = os.environ.get(endpoint_env)
    if auth_endpoint is None:
        error_and_exit(g_help("defect_env", endpoint_env), -1)
    headers = {"Content-Type": "application/json", "User-Agent": user_agent}
    url = "%s%s" % (auth_endpoint, url)
    if method == "GET":
        resp = requests.request(method, url, headers=headers, params=data)
    else:
        resp = requests.request(method, url, headers=headers, json=data)
    if resp.status_code != 200:
        error_and_exit("%s %s" % (url, resp.status_code))
    r_data = resp.json()
    if r_data["status"] % 10000 < 100:
        print(r_data["message"])
    else:
        error_and_exit(r_data["message"])
    return r_data
