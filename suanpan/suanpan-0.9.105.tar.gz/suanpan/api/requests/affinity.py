# coding=utf-8
from __future__ import absolute_import, print_function

from suanpan import g
from suanpan.api import requests


def getAffinityUrl(path, tls=g.hostTls):
    if g.affinity:
        return g.affinity + path

    if g.host:
        protocol = "https" if tls else "http"
        return "{}://{}{}".format(protocol, g.host, path)

    raise Exception("Suanpan API call Error: affinity and host not set")


def get(path, *args, **kwargs):
    return requests.get(getAffinityUrl(path), *args, **kwargs)


def post(path, *args, **kwargs):
    return requests.post(getAffinityUrl(path), *args, **kwargs)


def put(path, *args, **kwargs):
    return requests.put(getAffinityUrl(path), *args, **kwargs)


def delete(path, *args, **kwargs):
    return requests.delete(getAffinityUrl(path), *args, **kwargs)
